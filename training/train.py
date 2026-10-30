"""Train the square CNN and export the weights in the model_np.py format.

Usage:
  python train.py                       # data/synth/train.npz + val.npz, plus data/real/real.npz if present
  python train.py --epochs 20 --real-train-frac 0.5 --name model

Real scans are split by board: one part goes into training (oversampled with --real-weight)
and the rest is the validation set that counts toward the goal (>= 99.5 % per square).
With --real-train-frac 1 all of them are used for training (final model, no real validation).
"""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

import model_np
from common import CLASSES, DATA_DIR, MARGIN, OUT_DIR, PREPROCESS_VERSION, STORED, TILE, split_real

CROP_JITTER = 3  # px (at 32 scale) of random crop shift during training


class TileNet(nn.Module):
    """3 conv-conv-pool blocks + dense 64 + 13. With (8, 16, 32) channels: ~52k parameters and ~2.4 M
    multiplications per square (1/4 of the 16-32-64 width, which took several seconds on the phone)."""

    def __init__(self, widths=(8, 16, 32), hidden=64):
        super().__init__()
        layers, cin = [], 1
        for w in widths:
            for _ in range(2):
                layers += [nn.Conv2d(cin, w, 3, padding=1, bias=False), nn.BatchNorm2d(w), nn.ReLU(inplace=True)]
                cin = w
            layers.append(nn.MaxPool2d(2))
        self.features = nn.Sequential(*layers)
        side = TILE // 2 ** len(widths)
        self.fc1 = nn.Linear(cin * side * side, hidden)
        self.drop = nn.Dropout(0.2)
        self.fc2 = nn.Linear(hidden, len(CLASSES))

    def forward(self, x):
        x = self.features(x).flatten(1)
        return self.fc2(self.drop(F.relu(self.fc1(x))))


# ------------------------------------------------------------------- data

def load_npz(path):
    d = np.load(path)
    return d["x"], d["y"], (d["scan"] if "scan" in d else None)


def augment(xb: torch.Tensor, gen: torch.Generator) -> torch.Tensor:
    """xb: (B, STORED, STORED) uint8 -> (B, 1, 32, 32) float with shifted crop, flip and photometric jitter."""
    b = xb.shape[0]
    dx = torch.randint(MARGIN - CROP_JITTER, MARGIN + CROP_JITTER + 1, (b,), generator=gen)
    dy = torch.randint(MARGIN - CROP_JITTER, MARGIN + CROP_JITTER + 1, (b,), generator=gen)
    ar = torch.arange(TILE)
    rows = (dy[:, None] + ar[None, :])[:, :, None].expand(b, TILE, TILE)
    cols = (dx[:, None] + ar[None, :])[:, None, :].expand(b, TILE, TILE)
    x = xb[torch.arange(b)[:, None, None], rows, cols].float() / 255
    flip = torch.rand(b, generator=gen) < 0.5
    x[flip] = x[flip].flip(-1)
    gamma = torch.exp(torch.randn(b, 1, 1, generator=gen) * 0.2)
    x = x.clamp(1e-4, 1) ** gamma
    contrast = 1 + torch.randn(b, 1, 1, generator=gen) * 0.12
    shift = torch.randn(b, 1, 1, generator=gen) * 0.06
    x = (x - 0.5) * contrast + 0.5 + shift
    x = x + torch.randn(x.shape, generator=gen) * torch.rand(b, 1, 1, generator=gen) * 0.04
    return x.clamp(0, 1)[:, None]


def center(xb: np.ndarray) -> torch.Tensor:
    return torch.from_numpy(xb[:, MARGIN:MARGIN + TILE, MARGIN:MARGIN + TILE].astype(np.float32) / 255)[:, None]


@torch.no_grad()
def predict(model, x: np.ndarray, bs=2048) -> np.ndarray:
    model.eval()
    return np.concatenate([model(center(x[i:i + bs])).numpy() for i in range(0, len(x), bs)])


def report(name, logits, y, scan=None):
    pred = logits.argmax(1)
    acc = float((pred == y).mean())
    msg = f"{name}: {acc * 100:.3f} % ({int((pred != y).sum())} errors / {len(y)})"
    if scan is not None:
        boards = [bool((pred[scan == s] == y[scan == s]).all()) for s in np.unique(scan)]
        msg += f", perfect boards {sum(boards)}/{len(boards)}"
    return acc, msg


def confusions(logits, y, top=10):
    pred = logits.argmax(1)
    pairs = {}
    for t, p in zip(y[pred != y], pred[pred != y]):
        key = f"{CLASSES[t] or '.'}->{CLASSES[p] or '.'}"
        pairs[key] = pairs.get(key, 0) + 1
    return sorted(pairs.items(), key=lambda kv: -kv[1])[:top]


# ---------------------------------------------------------------- export

def export(model: TileNet, path_json: Path, metrics: dict, parity_x: np.ndarray):
    """Fold BatchNorm into the convolutions and write .bin + .json + .parity.json."""
    model.eval()
    chunks, layers, offset = [], [], 0

    def put(t: torch.Tensor):
        nonlocal offset
        a = t.detach().double().numpy().astype("<f4").ravel()
        chunks.append(a)
        ref = [offset, int(a.size)]
        offset += a.size
        return ref

    mods = list(model.features)
    i = 0
    while i < len(mods):
        m = mods[i]
        if isinstance(m, nn.Conv2d):
            bn = mods[i + 1]
            scale = bn.weight / torch.sqrt(bn.running_var + bn.eps)
            w = m.weight * scale[:, None, None, None]
            b = bn.bias - bn.running_mean * scale
            layers.append({"type": "conv2d", "in": m.in_channels, "out": m.out_channels, "kernel": m.kernel_size[0],
                           "pad": m.padding[0], "relu": True, "weight": put(w), "bias": put(b)})
            i += 3
        elif isinstance(m, nn.MaxPool2d):
            layers.append({"type": "maxpool2d", "size": m.kernel_size})
            i += 1
        else:
            raise RuntimeError(f"unexpected layer {m}")
    layers.append({"type": "flatten"})
    for fc, relu in ((model.fc1, True), (model.fc2, False)):
        layers.append({"type": "dense", "in": fc.in_features, "out": fc.out_features, "relu": relu,
                       "weight": put(fc.weight), "bias": put(fc.bias)})

    blob = np.concatenate(chunks)
    bin_path = path_json.with_suffix(".bin")
    path_json.parent.mkdir(parents=True, exist_ok=True)
    blob.tofile(bin_path)
    meta = {
        "format": model_np.FORMAT, "format_version": model_np.FORMAT_VERSION,
        "preprocess_version": PREPROCESS_VERSION,
        "created": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "input": [1, TILE, TILE], "classes": CLASSES,
        "weights_file": bin_path.name, "weights_count": int(blob.size),
        "sha256": hashlib.sha256(blob.tobytes()).hexdigest(),
        "layers": layers, "metrics": metrics,
    }
    path_json.write_text(json.dumps(meta, indent=1), encoding="utf-8")

    xin = center(parity_x)
    with torch.no_grad():
        logits = model(xin).numpy()
    par = {"inputs": np.round(xin[:, 0].numpy(), 6).tolist(), "logits": logits.tolist()}
    path_json.with_suffix(".parity.json").write_text(json.dumps(par), encoding="utf-8")
    diff = model_np.check_parity(path_json)
    print(f"exported {path_json} + {bin_path.name} ({blob.size} weights), numpy parity {diff:.2e}")


# ----------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--train", type=Path, nargs="+", default=[DATA_DIR / "synth" / "train.npz"])
    ap.add_argument("--val", type=Path, default=DATA_DIR / "synth" / "val.npz")
    ap.add_argument("--real", type=Path, default=DATA_DIR / "real" / "real.npz")
    ap.add_argument("--real-train-frac", type=float, default=0.5)
    ap.add_argument("--real-weight", type=int, default=20, help="times each real square is repeated per epoch")
    ap.add_argument("--epochs", type=int, default=14)
    ap.add_argument("--batch", type=int, default=256)
    ap.add_argument("--lr", type=float, default=3e-3)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--name", default="model")
    ap.add_argument("--widths", default="8,16,32", help="channels of the 3 conv blocks")
    a = ap.parse_args()

    torch.manual_seed(a.seed)
    torch.set_num_threads(os.cpu_count() or 4)
    gen = torch.Generator().manual_seed(a.seed)

    xs, ys = [], []
    for p in a.train:
        x, y, _ = load_npz(p)
        xs.append(x)
        ys.append(y)
    vx, vy, _ = load_npz(a.val)
    rx = ry = rscan = None
    if a.real.exists():
        rx, ry, rscan = load_npz(a.real)
        tr, va = split_real(rscan, a.real_train_frac, a.seed)
        if tr.any():
            xs.append(np.repeat(rx[tr], a.real_weight, axis=0))
            ys.append(np.repeat(ry[tr], a.real_weight))
        rx, ry, rscan = rx[va], ry[va], rscan[va]
        print(f"real: {int(tr.sum()) // 64} boards to training, {len(np.unique(rscan))} to validation")
        if not len(ry):
            rx = None
    else:
        print(f"no real data ({a.real} does not exist): synthetic validation only")
    tx = torch.from_numpy(np.concatenate(xs))
    ty = torch.from_numpy(np.concatenate(ys).astype(np.int64))
    assert tx.shape[1:] == (STORED, STORED)
    print(f"training: {len(ty)} squares; synthetic validation: {len(vy)}")

    model = TileNet(tuple(int(v) for v in a.widths.split(",")))
    print(f"parameters: {sum(p.numel() for p in model.parameters())}")
    opt = torch.optim.AdamW(model.parameters(), lr=a.lr, weight_decay=1e-4)
    steps = a.epochs * ((len(ty) + a.batch - 1) // a.batch)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=a.lr, total_steps=steps, pct_start=0.15)

    best, best_state, metrics = -1.0, None, {}
    for ep in range(1, a.epochs + 1):
        model.train()
        t0 = time.time()
        perm = torch.randperm(len(ty), generator=gen)
        total = 0.0
        for i in range(0, len(ty), a.batch):
            idx = perm[i:i + a.batch]
            out = model(augment(tx[idx], gen))
            loss = F.cross_entropy(out, ty[idx], label_smoothing=0.05)
            opt.zero_grad()
            loss.backward()
            opt.step()
            sched.step()
            total += loss.item() * len(idx)
        sacc, smsg = report("synthetic val", predict(model, vx), vy)
        line = f"epoch {ep:2d}  loss {total / len(ty):.4f}  {smsg}"
        score = sacc
        if rx is not None:
            racc, rmsg = report("real", predict(model, rx), ry, rscan)
            line += f"  |  {rmsg}"
            score = racc
        print(f"{line}  ({time.time() - t0:.0f} s)", flush=True)
        if score >= best:
            best = score
            best_state = {k: v.clone() for k, v in model.state_dict().items()}
            metrics = {"epoch": ep, "synthetic_val_acc": round(sacc, 6)}
            if rx is not None:
                metrics.update(real_val_acc=round(racc, 6), real_val_tiles=int(len(ry)))

    model.load_state_dict(best_state)
    print(f"best epoch {metrics['epoch']}: {metrics}")
    for name, (x, y) in {"synthetic val": (vx, vy), **({"real": (rx, ry)} if rx is not None else {})}.items():
        c = confusions(predict(model, x), y)
        if c:
            print(f"  confusions {name}: " + ", ".join(f"{k} x{v}" for k, v in c))
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    torch.save(best_state, OUT_DIR / f"{a.name}.pt")
    sample = np.random.default_rng(0).choice(len(vy), size=min(8, len(vy)), replace=False)
    export(model, OUT_DIR / f"{a.name}.json", metrics, vx[np.sort(sample)])


if __name__ == "__main__":
    main()
