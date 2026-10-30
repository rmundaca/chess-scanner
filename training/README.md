# Model training (PC only)

Nothing in this folder ships in the NAS package. It generates synthetic squares, prepares the real
ones exported from the app, trains a small CNN with PyTorch (CPU is enough) and exports the weights
to `out/model.json` + `out/model.bin`, which the NAS serves and `vision.js` runs in the browser.

These dependencies are separate from the app's (`package/requirements.txt`); see
`requirements.txt` in this folder.

## Setup (Windows)

```powershell
cd training
py -3.13 -m venv .venv
.\.venv\Scripts\pip install numpy pillow
.\.venv\Scripts\pip install torch --index-url https://download.pytorch.org/whl/cpu
.\.venv\Scripts\python -m unittest discover -s tests -t .
```

## Workflow

```powershell
# 1. Generator preview (out/preview/*.png)
.\.venv\Scripts\python synth.py --preview 12

# 2. Synthetic data (~7 min and ~10 min of CPU respectively)
.\.venv\Scripts\python synth.py --boards 10000 --out data/synth/train.npz
.\.venv\Scripts\python synth.py --boards 800 --seed 7 --keep-empty 1 --out data/synth/val.npz

# 3. Real data: copy the app export (History -> Export) into data/real/
.\.venv\Scripts\python prepare_real.py

# 4. Train and export (uses data/real/real.npz if present)
.\.venv\Scripts\python train.py
.\.venv\Scripts\python model_np.py out/model.json   # re-checks parity

# 5. Review mistakes on the real photos (out/errors/*.png; --all adds a sheet per board)
.\.venv\Scripts\python errors.py --all
```

An "error" with high confidence (> 90 %) is usually a wrong label in the app (a forgotten piece),
not a model failure: look at the image before changing the generator.

### Installing the model

- On the NAS, without repackaging: **Settings → Recognition → Upload model** and pick both
  `out/model.json` and `out/model.bin`. It is stored in `data/models/` and takes precedence over the built-in one.
- As the package's built-in model: copy both files to `package/app/model/` and build the package.

### Real data

`data/real/` accepts several ZIPs (`chess-scanner-dataset*.zip`); if a scan appears in more than one,
the most recent ZIP wins. `train.py` splits scans **by board**: with `--real-train-frac 0.5`
(default) half goes into training, oversampled `--real-weight` times, and the other half is the
validation set that measures the goal (>= 99.5 % per square). For the final model, once that figure
is known, retrain with `--real-train-frac 1`.

The photos are of copyrighted books: `data/` is in `.gitignore` and must not be published.

### More piece styles (fonts)

Any `.ttf`/`.otf` with the Unicode chess glyphs (U+2654-U+265F) placed in `fonts/` is used by the
generator alongside the app's own set and Segoe UI Symbol. They are only used to generate training
images; the fonts are not redistributed (`fonts/` is also ignored).

## Model contract

What `vision.js` must reproduce (preprocessing version 1, `common.py`):

1. Rectified 512×512 RGB board (the same `board.jpg` the app stores).
2. Gray `0.299 R + 0.587 G + 0.114 B` and 2×2 mean downscale to 256×256 (32×32 per square).
3. Levels: 256-bin histogram of `floor(gray)`; `lo` = first value with cumulative >= 1 %,
   `hi` = first value with cumulative >= 99 %; `x = clip((g - lo) / max(hi - lo, 16), 0, 1)`.
4. Each square (visual order, top row first) is one `(1, 32, 32)` input.
5. Output: 13 logits in `classes` order (`""` = empty, `PNBRQK`, `pnbrqk`); the piece color is
   as it appears, regardless of the diagram orientation.

Weight format (`model_np.py`): `model.json` describes the layers (`conv2d` 3×3 with padding 1 and
ReLU, `maxpool2d` 2, `flatten` in C,H,W order, `dense`) with `[offset, count]` in float32 elements
of `model.bin` (little-endian). BatchNorm is already folded into the convolutions. `model.parity.json`
holds 8 inputs with their expected logits for the JS parity test.

Architecture (default, `--widths 8,16,32`): 3 conv-conv-maxpool blocks (8, 16, 32 channels) +
dense 64 + dense 13: 51,717 weights (~200 KB) and ~2.4 M multiplications per square. It recognizes a
board in ~0.2 s on the PC (Node); on a phone it is estimated at under 1 s. The 16-32-64 version (138k weights)
had the same real accuracy but was 7 times slower.
