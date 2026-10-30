"""Run the exported model over the real scans and save the errors as images.

Usage:
  python errors.py                    # out/model.json on data/real/real.npz -> out/errors/
  python errors.py --all              # also save a contact sheet of each board

For each error: square with its context (40x40, enlarged), true label, prediction and confidence.
Shows whether the scan was in the training or validation part of the last train.py run
(same split as train.py with the same --real-train-frac and --seed).
"""
import argparse
import shutil

import numpy as np
from PIL import Image, ImageDraw

import model_np
from common import CLASSES, DATA_DIR, OUT_DIR, STORED, center_crop, split_real


def softmax(z):
    e = np.exp(z - z.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--model", default=str(OUT_DIR / "model.json"))
    ap.add_argument("--real", default=str(DATA_DIR / "real" / "real.npz"))
    ap.add_argument("--real-train-frac", type=float, default=0.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()

    meta, blob = model_np.load(a.model)
    d = np.load(a.real)
    x, y, scan = d["x"], d["y"], d["scan"]
    is_train, _ = split_real(scan, a.real_train_frac, a.seed)
    prob = softmax(model_np.forward(meta, blob, center_crop(x)))
    pred = prob.argmax(1)

    folder = OUT_DIR / "errors"
    shutil.rmtree(folder, ignore_errors=True)
    folder.mkdir(parents=True)
    name = lambda c: CLASSES[c] or "empty"
    for s in np.unique(scan):
        idx = np.where(scan == s)[0]
        part = "train" if is_train[idx[0]] else "val"
        wrong = idx[pred[idx] != y[idx]]
        low = idx[prob[idx].max(1) < 0.9]
        print(f"scan {s:4d} ({part:5s}): {len(wrong)} errors, {len(low)} squares with confidence < 90 %")
        for i in wrong:
            sq = i - idx[0]
            r, c = divmod(sq, 8)
            img = Image.fromarray(x[i]).resize((STORED * 5, STORED * 5), Image.NEAREST).convert("RGB")
            ImageDraw.Draw(img).rectangle((20, 20, 179, 179), outline=(255, 0, 0))
            fn = f"{s}_{part}_f{r}c{c}_{name(y[i])}_as_{name(pred[i])}_{prob[i, pred[i]] * 100:.0f}.png"
            img.save(folder / fn)
            print(f"    row {r} col {c} (visual): {name(y[i])} -> {name(pred[i])} ({prob[i, pred[i]] * 100:.0f} %)")
        if a.all:
            sheet = Image.new("RGB", (8 * 34, 8 * 34), (255, 255, 255))
            for k, i in enumerate(idx):
                t = Image.fromarray(x[i, 4:36, 4:36]).convert("RGB")
                if pred[i] != y[i]:
                    ImageDraw.Draw(t).rectangle((0, 0, 31, 31), outline=(255, 0, 0))
                sheet.paste(t, ((k % 8) * 34, (k // 8) * 34))
            sheet.resize((8 * 68, 8 * 68), Image.NEAREST).save(folder / f"{s}_{part}_board.png")
    print(f"total: {int((pred != y).sum())} errors in {len(y)} squares -> {folder}")


if __name__ == "__main__":
    main()
