"""Pieces, square order and preprocessing shared by the generator, real-data preparation,
training and the numpy reference. numpy + Pillow only.

The preprocessing is the contract with `vision.js`: any change here must be mirrored in JS
and bump `PREPROCESS_VERSION`. See training/README.md, section "Model contract".
"""
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent
APP_JS = ROOT.parent / "package" / "app" / "static" / "js" / "app.js"
DATA_DIR = ROOT / "data"
OUT_DIR = ROOT / "out"

# Class 0 = empty square. The order is part of the model format.
CLASSES = ["", "P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]
CLASS_INDEX = {c: i for i, c in enumerate(CLASSES)}

BOARD_SIZE = 512      # rectified board (same as BOARD_SIZE in app.js)
TILE = 32             # network input: 32x32 grayscale square
MARGIN = 4            # context kept around each square for shifted crops
STORED = TILE + 2 * MARGIN
PREPROCESS_VERSION = 1


def cells_from_placement(placement: str, flipped: bool) -> list:
    """64 squares in visual order (top image row first), like cellsFromPlacement in app.js."""
    arr = []
    for ch in placement.replace("/", ""):
        if ch.isdigit():
            arr.extend([""] * int(ch))
        else:
            arr.append(ch)
    if len(arr) != 64:
        raise ValueError(f"invalid placement: {placement}")
    return arr[::-1] if flipped else arr


def placement_from_cells(cells: list, flipped: bool = False) -> str:
    arr = cells[::-1] if flipped else list(cells)
    rows = []
    for r in range(8):
        row, empty = "", 0
        for ch in arr[r * 8:(r + 1) * 8]:
            if ch:
                row += (str(empty) if empty else "") + ch
                empty = 0
            else:
                empty += 1
        rows.append(row + (str(empty) if empty else ""))
    return "/".join(rows)


def board_gray(board_rgb: np.ndarray) -> np.ndarray:
    """512x512x3 uint8 board -> 256x256 float32 normalized to [0, 1].

    1. Gray: 0.299 R + 0.587 G + 0.114 B.
    2. 2x2 mean downscale (each square becomes 32x32).
    3. Levels: 256-bin histogram of floor(gray); lo = first value with cumulative >= 1 %,
       hi = first value with cumulative >= 99 %; x = clip((g - lo) / max(hi - lo, 16), 0, 1).
    """
    if board_rgb.shape[:2] != (BOARD_SIZE, BOARD_SIZE):
        raise ValueError("board must be 512x512")
    rgb = board_rgb.astype(np.float32)
    g = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]
    g = g.reshape(256, 2, 256, 2).mean(axis=(1, 3))
    hist = np.bincount(np.clip(g, 0, 255).astype(np.int32).ravel(), minlength=256)
    cum = np.cumsum(hist)
    n = cum[-1]
    lo = int(np.searchsorted(cum, 0.01 * n))
    hi = int(np.searchsorted(cum, 0.99 * n))
    return np.clip((g - lo) / max(hi - lo, 16), 0.0, 1.0).astype(np.float32)


def board_tiles(board_rgb: np.ndarray) -> np.ndarray:
    """512x512x3 board -> (64, STORED, STORED) uint8 in visual order, with MARGIN px of context
    (edges replicated). The center [MARGIN:MARGIN+TILE] is exactly the network input * 255."""
    g = board_gray(board_rgb)
    padded = np.pad(g, MARGIN, mode="edge")
    out = np.empty((64, STORED, STORED), np.uint8)
    for r in range(8):
        for c in range(8):
            y, x = r * TILE, c * TILE
            out[r * 8 + c] = np.round(padded[y:y + STORED, x:x + STORED] * 255)
    return out


def center_crop(tiles: np.ndarray) -> np.ndarray:
    """(N, STORED, STORED) uint8 -> (N, TILE, TILE) float32 in [0, 1]: the inference input."""
    return tiles[:, MARGIN:MARGIN + TILE, MARGIN:MARGIN + TILE].astype(np.float32) / 255.0


def load_board(path_or_file) -> np.ndarray:
    img = Image.open(path_or_file).convert("RGB")
    if img.size != (BOARD_SIZE, BOARD_SIZE):
        img = img.resize((BOARD_SIZE, BOARD_SIZE), Image.BILINEAR)
    return np.asarray(img)


def homography(src, dst) -> np.ndarray:
    """3x3 matrix mapping 4 src points to 4 dst points."""
    a = []
    b = []
    for (x, y), (X, Y) in zip(src, dst):
        a.append([x, y, 1, 0, 0, 0, -x * X, -y * X])
        a.append([0, 0, 0, x, y, 1, -x * Y, -y * Y])
        b.extend([X, Y])
    h = np.linalg.solve(np.array(a, np.float64), np.array(b, np.float64))
    return np.append(h, 1.0).reshape(3, 3)


def warp_quad(img: Image.Image, quad, size: int = BOARD_SIZE) -> Image.Image:
    """Rectify the quadrilateral `quad` ([tl, tr, br, bl] in img px) to a size x size square."""
    h = homography([(0, 0), (size, 0), (size, size), (0, size)], quad)
    return img.transform((size, size), Image.PERSPECTIVE, tuple(h.ravel()[:8]), Image.BILINEAR)


def split_real(scan, frac, seed):
    """Split real scans by board: (training mask, validation mask)."""
    ids = np.unique(scan)
    rng = np.random.default_rng(seed)
    rng.shuffle(ids)
    if len(ids) < 2 and frac < 1:
        return np.zeros(len(scan), bool), np.ones(len(scan), bool)
    n_train = int(round(len(ids) * frac))
    train_ids = set(ids[:n_train].tolist())
    is_train = np.array([s in train_ids for s in scan])
    return is_train, ~is_train
