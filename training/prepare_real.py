"""Convert the app export (History -> Export) into labeled squares.

Usage:
  python prepare_real.py                                  # all ZIPs in data/real/
  python prepare_real.py path/chess-scanner-dataset.zip   # one or more specific ZIPs

Reads labels.json and scans/<id>/board.jpg from each ZIP and writes data/real/real.npz with:
  x: (N, 40, 40) uint8   square with 4 px of context (see common.board_tiles)
  y: (N,) uint8          class (common.CLASSES)
  scan: (N,) int32       scan id, to split training and validation by board
If several ZIPs repeat an id, the last one wins (exports are cumulative).
"""
import argparse
import json
import zipfile
from pathlib import Path

import numpy as np

from common import CLASS_INDEX, DATA_DIR, board_tiles, cells_from_placement, load_board

REAL_DIR = DATA_DIR / "real"


def read_zip(path: Path) -> dict:
    boards = {}
    with zipfile.ZipFile(path) as zf:
        labels = json.loads(zf.read("labels.json"))
        for item in labels:
            name = (item.get("files") or {}).get("board")
            if not name:
                continue
            with zf.open(name) as f:
                board = load_board(f)
            boards[item["id"]] = (cells_from_placement(item["placement"], item.get("flipped", False)), board, item)
    return boards


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("zips", nargs="*", type=Path)
    ap.add_argument("--out", type=Path, default=REAL_DIR / "real.npz")
    a = ap.parse_args()
    zips = a.zips or sorted(REAL_DIR.glob("*.zip"), key=lambda p: p.stat().st_mtime)
    if not zips:
        raise SystemExit(f"No ZIP found. Copy the app export into {REAL_DIR}")

    boards = {}
    for z in zips:
        found = read_zip(z)
        print(f"{z.name}: {len(found)} boards")
        boards.update(found)

    xs, ys, ss = [], [], []
    for scan_id in sorted(boards):
        cells, board, _ = boards[scan_id]
        xs.append(board_tiles(board))
        ys.extend(CLASS_INDEX[c] for c in cells)
        ss.extend([scan_id] * 64)
    x = np.concatenate(xs)
    y = np.array(ys, np.uint8)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(a.out, x=x, y=y, scan=np.array(ss, np.int32))
    counts = np.bincount(y, minlength=13)
    print(f"{len(boards)} boards, {len(y)} squares ({len(y) - counts[0]} with a piece) -> {a.out}")


if __name__ == "__main__":
    main()
