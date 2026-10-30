"""Synthetic book-diagram generator -> labeled squares.

Each sample follows the same path as a real photo in the app:
  printed page (board, frame, coordinates, text) -> "photo" (perspective, lighting, blur,
  noise, JPEG) -> rectified to 512x512 with slightly inaccurate corners -> JPEG 0.92 -> squares.

Usage:
  python synth.py --boards 8000 --out data/synth/train.npz
  python synth.py --boards 600 --seed 7 --out data/synth/val.npz --keep-empty 1
  python synth.py --preview 12          # sample PNGs in out/preview/
"""
import argparse
import io
import math
import os
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

import pieces
from common import CLASS_INDEX, OUT_DIR, ROOT, board_tiles, warp_quad

LABEL_FONTS = [Path("C:/Windows/Fonts/arial.ttf"), Path("C:/Windows/Fonts/times.ttf"),
               Path("C:/Windows/Fonts/georgia.ttf"), Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf")]
PIECE_WEIGHTS = {"P": 8, "N": 2, "B": 2, "R": 2, "Q": 1.2, "K": 1.5}

_FONT_SOURCES = None


def font_sources():
    global _FONT_SOURCES
    if _FONT_SOURCES is None:
        _FONT_SOURCES = [str(p) for p in pieces.font_paths() if pieces.font_has_chess(p)]
    return _FONT_SOURCES


# ----------------------------------------------------------------- position

def random_cells(rng) -> list:
    n = int(rng.choice([rng.integers(0, 8), rng.integers(6, 20), rng.integers(16, 33)], p=[0.25, 0.45, 0.30]))
    kinds = list(PIECE_WEIGHTS)
    w = np.array([PIECE_WEIGHTS[k] for k in kinds])
    cells = [""] * 64
    for sq in rng.choice(64, size=n, replace=False):
        k = kinds[rng.choice(len(kinds), p=w / w.sum())]
        cells[sq] = k if rng.random() < 0.5 else k.lower()
    return cells


# --------------------------------------------------------------------- page

def _hatch(draw, size, rng, ink, scale):
    style = rng.choice(["diag", "diag", "diag", "anti", "cross", "horiz", "dots"])
    spacing = rng.uniform(2.6, 6.5) * scale
    width = max(1, round(rng.uniform(0.5, 1.5) * scale))
    if style == "dots":
        r = max(1.0, width * 0.7)
        for y in np.arange(0, size, spacing):
            off = spacing / 2 if int(y / spacing) % 2 else 0
            for x in np.arange(off, size, spacing):
                draw.ellipse((x - r, y - r, x + r, y + r), fill=ink)
        return
    dirs = {"diag": [1], "anti": [-1], "cross": [1, -1], "horiz": [0]}[style]
    for d in dirs:
        if d == 0:
            for y in np.arange(0, size, spacing):
                draw.line((0, y, size, y), fill=ink, width=width)
            continue
        step = spacing * math.sqrt(2)
        for t in np.arange(-size, size * 2, step):
            if d > 0:
                draw.line((t, size, t + size, 0), fill=ink, width=width)
            else:
                draw.line((t, 0, t + size, size), fill=ink, width=width)


def render_page(cells, rng, ss=2):
    """Printed page in RGB and the 4 corners of the squares area (page px)."""
    sq = int(rng.integers(34, 78)) * ss
    board = sq * 8
    margin = int(sq * rng.uniform(0.7, 1.8))
    size = board + 2 * margin
    paper = np.array([rng.uniform(232, 255)] * 3) - np.array([0, rng.uniform(0, 8), rng.uniform(0, 18)])
    paper = tuple(int(v) for v in paper)
    ink_v = int(rng.uniform(0, 55))
    ink = (ink_v, ink_v, ink_v + int(rng.uniform(0, 10)))
    page = Image.new("RGB", (size, size), paper)
    draw = ImageDraw.Draw(page)
    x0 = y0 = margin

    # Dark squares
    shade = rng.choice(["hatch", "hatch", "hatch", "gray", "gray", "none"], p=[0.25, 0.2, 0.15, 0.17, 0.15, 0.08])
    dark_mask = Image.new("L", (board, board), 0)
    dm = ImageDraw.Draw(dark_mask)
    for r in range(8):
        for c in range(8):
            if (r + c) % 2 == 1:
                dm.rectangle((c * sq, r * sq, (c + 1) * sq - 1, (r + 1) * sq - 1), fill=255)
    if shade == "hatch":
        tex = Image.new("RGB", (board, board), paper)
        _hatch(ImageDraw.Draw(tex), board, rng, ink, ss)
        page.paste(tex, (x0, y0), dark_mask)
    elif shade == "gray":
        g = int(rng.uniform(110, 215))
        page.paste((g, g, g + int(rng.uniform(-6, 6))), (x0, y0), dark_mask)
    if rng.random() < 0.06:  # grayish light squares
        g = int(rng.uniform(205, 235))
        page.paste((g, g, g), (x0, y0), Image.eval(dark_mask, lambda v: 255 - v))
    if shade == "none" or rng.random() < 0.12:  # thin grid
        lw = max(1, round(rng.uniform(0.5, 1.2) * ss))
        for i in range(1, 8):
            draw.line((x0 + i * sq, y0, x0 + i * sq, y0 + board), fill=ink, width=lw)
            draw.line((x0, y0 + i * sq, x0 + board, y0 + i * sq), fill=ink, width=lw)

    # Frame
    if rng.random() < 0.92:
        fw = max(1, round(rng.uniform(0.6, 7) * ss))
        gap = round(rng.uniform(0, 4) * ss) if rng.random() < 0.3 else 0
        o = gap + fw / 2
        draw.rectangle((x0 - o, y0 - o, x0 + board + o - 1, y0 + board + o - 1), outline=ink, width=fw)
        if gap and rng.random() < 0.5:
            draw.rectangle((x0, y0, x0 + board - 1, y0 + board - 1), outline=ink, width=max(1, ss // 2))

    # Coordinates
    if rng.random() < 0.5:
        fonts = [p for p in LABEL_FONTS if p.exists()]
        f = ImageFont.truetype(str(fonts[rng.integers(len(fonts))]), int(sq * rng.uniform(0.22, 0.38))) if fonts else ImageFont.load_default()
        files = "abcdefgh" if rng.random() < 0.8 else "hgfedcba"
        ranks = "87654321" if files[0] == "a" else "12345678"
        pad = sq * 0.32
        for i in range(8):
            draw.text((x0 + i * sq + sq / 2, y0 + board + pad), files[i], font=f, fill=ink, anchor="mm")
            draw.text((x0 - pad, y0 + i * sq + sq / 2), ranks[i], font=f, fill=ink, anchor="mm")

    # Surrounding text (lines of "words")
    for _ in range(int(rng.integers(0, 6))):
        top = rng.random() < 0.5
        y = rng.uniform(2, margin * 0.45) if top else rng.uniform(size - margin * 0.45, size - 6)
        x = rng.uniform(0, size * 0.2)
        h = sq * rng.uniform(0.12, 0.22)
        while x < size - sq * 0.3:
            w = sq * rng.uniform(0.2, 0.9)
            draw.rectangle((x, y, x + w, y + h), fill=ink)
            x += w + sq * rng.uniform(0.12, 0.25)

    # Pieces
    fonts = font_sources()
    use_font = fonts and rng.random() < 0.45
    font_path = fonts[rng.integers(len(fonts))] if use_font else None
    stroke = rng.uniform(1.1, 2.4)
    scale = rng.uniform(0.78, 0.98)
    px = max(8, int(sq * scale))
    cache = {}
    for i, ch in enumerate(cells):
        if not ch:
            continue
        if ch not in cache:
            cache[ch] = (pieces.render_font_piece(font_path, ch, px) if use_font
                         else pieces.render_app_piece(ch, px, stroke=stroke))
        ink_m, paper_m = cache[ch]
        r, c = divmod(i, 8)
        jx, jy = rng.normal(0, sq * 0.015, 2)
        ox = int(x0 + c * sq + (sq - px) / 2 + jx)
        oy = int(y0 + r * sq + (sq - px) / 2 + jy + sq * rng.uniform(-0.01, 0.03))
        page.paste(paper, (ox, oy), paper_m)
        page.paste(ink, (ox, oy), ink_m)

    page = page.resize((size // ss, size // ss), Image.LANCZOS)
    k = 1 / ss
    corners = [(x0 * k, y0 * k), ((x0 + board) * k, y0 * k), ((x0 + board) * k, (y0 + board) * k), (x0 * k, (y0 + board) * k)]
    return page, corners


# -------------------------------------------------------------------- photo

def _project(h, pts):
    out = []
    for x, y in pts:
        v = h @ np.array([x, y, 1.0])
        out.append((v[0] / v[2], v[1] / v[2]))
    return out


def take_photo(page, corners, rng):
    """Simulate the phone photo. Returns the photo and the true board corners in it."""
    from common import homography
    b = rng.uniform(300, 1150)          # approximate board side in the photo (px)
    canvas = int(b * rng.uniform(1.25, 1.6))
    cx = cy = canvas / 2
    ang = math.radians(rng.normal(0, 3.5))
    base = [(-b / 2, -b / 2), (b / 2, -b / 2), (b / 2, b / 2), (-b / 2, b / 2)]
    persp = rng.uniform(0, 0.09)
    dst = []
    for x, y in base:
        x += rng.normal(0, persp) * b
        y += rng.normal(0, persp) * b
        dst.append((cx + x * math.cos(ang) - y * math.sin(ang), cy + x * math.sin(ang) + y * math.cos(ang)))
    h = homography(corners, dst)                 # page -> photo
    inv = np.linalg.inv(h)
    inv /= inv[2, 2]
    bg = tuple(int(v) for v in rng.uniform(20, 120, 3))
    photo = page.transform((canvas, canvas), Image.PERSPECTIVE, tuple(inv.ravel()[:8]), Image.BICUBIC, fillcolor=bg)

    arr = np.asarray(photo).astype(np.float32)
    # Uneven lighting: smooth field + gradient, and sometimes a shadow
    field = rng.uniform(0.7, 1.05, (3, 3)).astype(np.float32)
    field = np.asarray(Image.fromarray((field * 100).astype(np.uint8)).resize((canvas, canvas), Image.BICUBIC)).astype(np.float32) / 100
    gx = np.linspace(-1, 1, canvas, dtype=np.float32)
    grad = 1 + rng.uniform(-0.15, 0.15) * gx[None, :] + rng.uniform(-0.15, 0.15) * gx[:, None]
    light = field * grad
    if rng.random() < 0.3:
        sh = Image.new("L", (canvas, canvas), 0)
        p0 = rng.uniform(0, canvas, 2)
        ImageDraw.Draw(sh).polygon([tuple(p0), tuple(rng.uniform(0, canvas, 2)), (canvas, canvas), (0, canvas)], fill=255)
        sh = np.asarray(sh.filter(ImageFilter.GaussianBlur(canvas * 0.05))).astype(np.float32) / 255
        light *= 1 - sh * rng.uniform(0.15, 0.45)
    tint = np.array([1.0, rng.uniform(0.95, 1.02), rng.uniform(0.85, 1.02)], np.float32)
    arr = arr * light[..., None] * tint
    arr += rng.normal(0, rng.uniform(0, 7), arr.shape).astype(np.float32)
    photo = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))
    blur = rng.uniform(0, 1.3) * b / 600
    if blur > 0.25:
        photo = photo.filter(ImageFilter.GaussianBlur(blur))
    buf = io.BytesIO()
    photo.save(buf, "JPEG", quality=int(rng.uniform(45, 95)))
    buf.seek(0)
    return Image.open(buf).convert("RGB"), dst


def to_board(photo, quad, rng):
    """Rectify with the typical manual corner-adjustment error and the app's JPEG 0.92."""
    side = math.dist(quad[0], quad[2]) / math.sqrt(2)
    err = rng.uniform(0.002, 0.009) * side
    user = [(x + rng.normal(0, err), y + rng.normal(0, err)) for x, y in quad]
    board = warp_quad(photo, user)
    buf = io.BytesIO()
    board.save(buf, "JPEG", quality=92)
    buf.seek(0)
    return np.asarray(Image.open(buf).convert("RGB"))


def sample(rng):
    cells = random_cells(rng)
    page, corners = render_page(cells, rng)
    photo, quad = take_photo(page, corners, rng)
    return cells, page, photo, to_board(photo, quad, rng)


# ---------------------------------------------------------------- dataset

def _worker(args):
    seed, n, keep_empty = args
    rng = np.random.default_rng(seed)
    xs, ys = [], []
    for _ in range(n):
        cells, _, _, board = sample(rng)
        tiles = board_tiles(board)
        for i, ch in enumerate(cells):
            if ch or rng.random() < keep_empty:
                xs.append(tiles[i])
                ys.append(CLASS_INDEX[ch])
    return np.stack(xs), np.array(ys, np.uint8)


def build(boards, seed, keep_empty, out, workers):
    chunk = 50
    jobs = [(seed * 100003 + i, min(chunk, boards - i * chunk), keep_empty) for i in range(math.ceil(boards / chunk))]
    t0 = time.time()
    xs, ys = [], []
    with Pool(workers) as pool:
        for k, (x, y) in enumerate(pool.imap_unordered(_worker, jobs), 1):
            xs.append(x)
            ys.append(y)
            print(f"\r  {min(k * chunk, boards)}/{boards} boards  {time.time() - t0:5.0f} s", end="", flush=True)
    print()
    x, y = np.concatenate(xs), np.concatenate(ys)
    out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(out, x=x, y=y)
    counts = np.bincount(y, minlength=13)
    print(f"  {len(y)} squares -> {out}  (empty {counts[0]}, pieces {len(y) - counts[0]})")


def preview(n, seed):
    folder = OUT_DIR / "preview"
    folder.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(seed)
    print("Unicode fonts:", font_sources() or "none")
    for i in range(n):
        cells, page, photo, board = sample(rng)
        photo.save(folder / f"{i:02d}_photo.jpg", quality=90)
        Image.fromarray(board).save(folder / f"{i:02d}_board.png")
    print(f"{n} samples in {folder}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--boards", type=int, default=8000)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--keep-empty", type=float, default=0.3, help="fraction of empty squares to keep")
    ap.add_argument("--out", type=Path, default=ROOT / "data" / "synth" / "train.npz")
    ap.add_argument("--workers", type=int, default=max(1, (os.cpu_count() or 2) - 1))
    ap.add_argument("--preview", type=int, default=0, help="only generate N sample images")
    a = ap.parse_args()
    if a.preview:
        preview(a.preview, a.seed)
    else:
        build(a.boards, a.seed, a.keep_empty, a.out, a.workers)


if __name__ == "__main__":
    main()
