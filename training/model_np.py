"""Model weight format and numpy reference forward pass (what `vision.js` must replicate).

Files: <name>.json (description) + <name>.bin (float32 little-endian, all tensors
concatenated). In each layer `weight` and `bias` are [offset, count] in float32 elements.
- conv2d: weight [out][in][k][k], stride 1, zero padding `pad`; then ReLU if `relu`.
- maxpool2d: window and stride `size`.
- flatten: channel, row, column order (C, H, W).
- dense: weight [out][in]; then ReLU if `relu`.
The output is logits (no softmax). The input is (1, 32, 32) in [0, 1] (common.board_gray).

Usage:  python model_np.py out/model.json      # checks the parity file <name>.parity.json
"""
import json
import sys
from pathlib import Path

import numpy as np

FORMAT = "chess-scanner-cnn"
FORMAT_VERSION = 1


def load(json_path: Path):
    json_path = Path(json_path)
    meta = json.loads(json_path.read_text(encoding="utf-8"))
    if meta.get("format") != FORMAT or meta.get("format_version") != FORMAT_VERSION:
        raise ValueError("unsupported model format")
    blob = np.fromfile(json_path.with_name(meta["weights_file"]), dtype="<f4")
    if blob.size != meta["weights_count"]:
        raise ValueError("wrong weights size")
    return meta, blob


def _take(blob, ref):
    off, n = ref
    return blob[off:off + n]


def forward(meta, blob, x: np.ndarray) -> np.ndarray:
    """x: (N, 32, 32) or (N, 1, 32, 32) float32 -> logits (N, classes)."""
    a = x.astype(np.float32)
    if a.ndim == 3:
        a = a[:, None]
    for layer in meta["layers"]:
        t = layer["type"]
        if t == "conv2d":
            k, p = layer["kernel"], layer["pad"]
            w = _take(blob, layer["weight"]).reshape(layer["out"], layer["in"], k, k)
            b = _take(blob, layer["bias"])
            ap = np.pad(a, ((0, 0), (0, 0), (p, p), (p, p)))
            win = np.lib.stride_tricks.sliding_window_view(ap, (k, k), axis=(2, 3))  # N,C,H,W,k,k
            a = np.einsum("nchwij,ocij->nohw", win, w, optimize=True) + b[None, :, None, None]
        elif t == "maxpool2d":
            s = layer["size"]
            n, c, h, w_ = a.shape
            a = a[:, :, :h // s * s, :w_ // s * s].reshape(n, c, h // s, s, w_ // s, s).max(axis=(3, 5))
        elif t == "flatten":
            a = a.reshape(a.shape[0], -1)
        elif t == "dense":
            w = _take(blob, layer["weight"]).reshape(layer["out"], layer["in"])
            a = a @ w.T + _take(blob, layer["bias"])
        else:
            raise ValueError(f"unknown layer: {t}")
        if layer.get("relu"):
            a = np.maximum(a, 0)
    return a


def check_parity(json_path: Path, tol: float = 1e-3) -> float:
    meta, blob = load(json_path)
    par = json.loads(Path(json_path).with_suffix(".parity.json").read_text(encoding="utf-8"))
    x = np.array(par["inputs"], np.float32).reshape(-1, 32, 32)
    got = forward(meta, blob, x)
    diff = float(np.abs(got - np.array(par["logits"], np.float32)).max())
    if diff > tol:
        raise AssertionError(f"parity failed: max difference {diff:.2e}")
    return diff


if __name__ == "__main__":
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "out/model.json")
    print(f"numpy parity OK (max difference {check_parity(path):.2e})")
