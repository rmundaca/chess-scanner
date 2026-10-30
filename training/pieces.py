"""Piece rasterization for the synthetic generator.

Two piece sources:
- The app's own SVG set (`PIECE_SHAPES` in app.js), read from app.js itself to avoid duplicating it.
- TTF/OTF fonts with the Unicode chess glyphs (U+2654..U+265F): any in training/fonts/ and,
  if present, Windows Segoe UI Symbol. Used for training only; not redistributed.

Each piece is returned as two L masks (0..255) of the same size: `ink` (dark stroke/fill)
and `paper` (silhouette that covers the square background with paper), ready to composite.
"""
import math
import re
from functools import lru_cache
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from common import APP_JS, ROOT

FONTS_DIR = ROOT / "fonts"
SYSTEM_FONTS = [Path("C:/Windows/Fonts/seguisym.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
UNICODE_WHITE = {"k": "\u2654", "q": "\u2655", "r": "\u2656", "b": "\u2657", "n": "\u2658", "p": "\u2659"}
UNICODE_BLACK = {"k": "\u265a", "q": "\u265b", "r": "\u265c", "b": "\u265d", "n": "\u265e", "p": "\u265f"}

VIEWBOX = 45.0


# ----------------------------------------------------------------- app SVG set

@lru_cache(maxsize=1)
def app_shapes() -> dict:
    """{'p': [('pb', [element, ...]), ...], ...} from the PIECE_SHAPES block in app.js."""
    src = APP_JS.read_text(encoding="utf-8")
    block = re.search(r"const PIECE_SHAPES = \{(.*?)\n\};", src, re.S)
    if not block:
        raise RuntimeError("PIECE_SHAPES not found in app.js")
    shapes = {}
    for m in re.finditer(r"\n    ([a-z]): \[(.*?)\n    \],", block.group(1), re.S):
        parts = []
        for cls, svg in re.findall(r"\['(\w+)', '(.*?)'\]", m.group(2)):
            elems = re.findall(r"<(circle|rect|path)\b([^>]*)/>", svg)
            parts.append((cls, [(tag, dict(re.findall(r'([\w-]+)="([^"]*)"', attrs))) for tag, attrs in elems]))
        shapes[m.group(1)] = parts
    if set(shapes) != set("pnbrqk"):
        raise RuntimeError(f"PIECE_SHAPES incomplete: {sorted(shapes)}")
    return shapes


_NUM = re.compile(r"[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")
_TOKEN = re.compile(r"[MmLlHhVvCcSsQqZz]|[-+]?(?:\d+\.?\d*|\.\d+)(?:[eE][-+]?\d+)?")


def _cubic(p0, p1, p2, p3, n=12):
    pts = []
    for i in range(1, n + 1):
        t = i / n
        u = 1 - t
        pts.append((u ** 3 * p0[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t ** 3 * p3[0],
                    u ** 3 * p0[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t ** 3 * p3[1]))
    return pts


def parse_path(d: str) -> list:
    """d attribute -> list of subpaths [(points, closed)]. Supports M L H V C S Q Z (abs/rel)."""
    tokens = _TOKEN.findall(d)
    subpaths, pts = [], []
    cur = (0.0, 0.0)
    start = cur
    last_ctrl = None
    cmd = None
    i = 0

    def num():
        nonlocal i
        v = float(tokens[i])
        i += 1
        return v

    while i < len(tokens):
        if tokens[i].isalpha():
            cmd = tokens[i]
            i += 1
            if cmd in "Zz":
                if pts:
                    subpaths.append((pts, True))
                pts, cur, last_ctrl = [], start, None
                continue
        rel = cmd.islower()
        c = cmd.upper()
        ox, oy = cur if rel else (0.0, 0.0)
        if c == "M":
            if pts:
                subpaths.append((pts, False))
            cur = (ox + num(), oy + num())
            start = cur
            pts = [cur]
            cmd = "l" if rel else "L"  # extra coordinates after M are implicit L
            last_ctrl = None
        elif c == "L":
            cur = (ox + num(), oy + num())
            pts.append(cur)
            last_ctrl = None
        elif c == "H":
            cur = ((ox if rel else 0.0) + num(), cur[1])
            pts.append(cur)
            last_ctrl = None
        elif c == "V":
            cur = (cur[0], (oy if rel else 0.0) + num())
            pts.append(cur)
            last_ctrl = None
        elif c == "C":
            p1 = (ox + num(), oy + num())
            p2 = (ox + num(), oy + num())
            p3 = (ox + num(), oy + num())
            pts.extend(_cubic(cur, p1, p2, p3))
            cur, last_ctrl = p3, p2
        elif c == "S":
            p1 = (2 * cur[0] - last_ctrl[0], 2 * cur[1] - last_ctrl[1]) if last_ctrl else cur
            p2 = (ox + num(), oy + num())
            p3 = (ox + num(), oy + num())
            pts.extend(_cubic(cur, p1, p2, p3))
            cur, last_ctrl = p3, p2
        elif c == "Q":
            q = (ox + num(), oy + num())
            p3 = (ox + num(), oy + num())
            p1 = (cur[0] + 2 / 3 * (q[0] - cur[0]), cur[1] + 2 / 3 * (q[1] - cur[1]))
            p2 = (p3[0] + 2 / 3 * (q[0] - p3[0]), p3[1] + 2 / 3 * (q[1] - p3[1]))
            pts.extend(_cubic(cur, p1, p2, p3))
            cur, last_ctrl = p3, None
        else:
            raise ValueError(f"unsupported SVG command: {cmd}")
    if pts:
        subpaths.append((pts, False))
    return subpaths


def _rounded_rect(x, y, w, h, r, n=6):
    r = min(r, w / 2, h / 2)
    if r <= 0:
        return [(x, y), (x + w, y), (x + w, y + h), (x, y + h)]
    pts = []
    for cx, cy, a0 in ((x + w - r, y + r, -90), (x + w - r, y + h - r, 0), (x + r, y + h - r, 90), (x + r, y + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n)
            pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts


def _element_polys(tag, attrs) -> list:
    if tag == "circle":
        cx, cy, r = float(attrs["cx"]), float(attrs["cy"]), float(attrs["r"])
        return [([(cx + r * math.cos(2 * math.pi * k / 32), cy + r * math.sin(2 * math.pi * k / 32)) for k in range(32)], True)]
    if tag == "rect":
        return [(_rounded_rect(float(attrs["x"]), float(attrs["y"]), float(attrs["width"]),
                               float(attrs["height"]), float(attrs.get("rx", 0))), True)]
    return parse_path(attrs["d"])


def render_app_piece(ch: str, px: int, stroke: float = 1.5, ss: int = 4):
    """Piece from the app set at px x px. stroke in viewBox units (the app uses 1.5)."""
    white = ch.isupper()
    big = px * ss
    k = big / VIEWBOX
    ink = Image.new("L", (big, big), 0)      # 255 = dark ink
    paper = Image.new("L", (big, big), 0)    # 255 = paper (covers the background)
    di, dp = ImageDraw.Draw(ink), ImageDraw.Draw(paper)
    w = max(1, round(stroke * k))
    for cls, elems in app_shapes()[ch.lower()]:
        for tag, attrs in elems:
            dot = "dot" in attrs.get("class", "")
            for pts, closed in _element_polys(tag, attrs):
                sp = [(x * k, y * k) for x, y in pts]
                if cls == "pb":
                    dp.polygon(sp, fill=255)
                    if white:
                        di.polygon(sp, fill=0)
                    else:
                        di.polygon(sp, fill=255)
                    di.line(sp + [sp[0]], fill=255, width=w, joint="curve")
                    dp.line(sp + [sp[0]], fill=255, width=w, joint="curve")
                else:  # detail in contrasting color
                    val = 255 if white else 0
                    if dot or closed and tag != "path":
                        di.polygon(sp, fill=val)
                    else:
                        di.line(sp, fill=val, width=w)
                        r = w / 2  # rounded ends (stroke-linecap: round)
                        for x, y in (sp[0], sp[-1]):
                            di.ellipse((x - r, y - r, x + r, y + r), fill=val)
    return ink.resize((px, px), Image.LANCZOS), paper.resize((px, px), Image.LANCZOS)


# ------------------------------------------------------------ Unicode fonts

def font_paths() -> list:
    paths = sorted(p for p in FONTS_DIR.glob("*") if p.suffix.lower() in (".ttf", ".otf"))
    return paths + [p for p in SYSTEM_FONTS if p.exists()]


@lru_cache(maxsize=64)
def _font(path: str, size: int):
    return ImageFont.truetype(path, size)


def font_has_chess(path: Path) -> bool:
    try:
        f = _font(str(path), 64)
        a, b = f.getmask("\u265a"), f.getmask("\u2654")
        # Without the glyphs both render as the same .notdef
        return bool(a.getbbox()) and bytes(a) != bytes(b)
    except OSError:
        return False


def _glyph(path: str, text: str, px: int, ss: int):
    big = px * ss
    f = _font(path, int(big * 0.86))
    img = Image.new("L", (big, big), 0)
    d = ImageDraw.Draw(img)
    x0, y0, x1, y1 = d.textbbox((0, 0), text, font=f, anchor="ls")
    d.text(((big - (x1 - x0)) / 2 - x0, (big - (y1 - y0)) / 2 - y0), text, font=f, fill=255, anchor="ls")
    return img


def render_font_piece(path: str, ch: str, px: int, ss: int = 2):
    """Piece from a Unicode font. The silhouette (paper) is taken from the filled black glyph."""
    kind = ch.lower()
    solid = _glyph(path, UNICODE_BLACK[kind], px, ss)
    # Dilate the silhouette slightly: leaves a paper halo and covers small differences with the white glyph
    paper = solid.filter(ImageFilter.MaxFilter(3))
    ink = solid if ch.islower() else _glyph(path, UNICODE_WHITE[kind], px, ss)
    # Fonts have their own margins: scale so the king fills the square as in the SVG set
    # (one scale per font, so the pawn stays shorter than the king)
    box = paper.getbbox() or (0, 0, paper.width, paper.height)
    ink, paper = ink.crop(box), paper.crop(box)
    big = px * ss
    king = _glyph(path, UNICODE_BLACK["k"], px, ss).getbbox() or box
    k = min(big * 0.92 / max(king[2] - king[0], king[3] - king[1]), big * 0.96 / max(ink.width, ink.height))
    w, h = max(1, round(ink.width * k)), max(1, round(ink.height * k))
    out = []
    for m in (ink, paper):
        canvas = Image.new("L", (big, big), 0)
        canvas.paste(m.resize((w, h), Image.LANCZOS), ((big - w) // 2, big - h - round(big * 0.05)))
        out.append(canvas.resize((px, px), Image.LANCZOS))
    return out[0], out[1]
