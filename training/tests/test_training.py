import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

import model_np
import pieces
from common import STORED, board_gray, board_tiles, cells_from_placement, placement_from_cells


class CommonTests(unittest.TestCase):
    def test_placement_roundtrip_and_flip(self):
        start = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
        cells = cells_from_placement(start, False)
        self.assertEqual(cells[0], "r")
        self.assertEqual(cells[60], "K")
        flipped = cells_from_placement(start, True)
        self.assertEqual(flipped[0], "R")    # black at the bottom: h1 ends up top-left
        self.assertEqual(flipped[3], "K")
        self.assertEqual(placement_from_cells(flipped, True), start)
        self.assertEqual(placement_from_cells(cells), start)

    def test_tiles_shape_and_levels(self):
        rng = np.random.default_rng(0)
        board = rng.integers(60, 200, (512, 512, 3), dtype=np.uint8)
        g = board_gray(board)
        self.assertEqual(g.shape, (256, 256))
        self.assertAlmostEqual(float(g.min()), 0.0)
        self.assertAlmostEqual(float(g.max()), 1.0)
        tiles = board_tiles(board)
        self.assertEqual(tiles.shape, (64, STORED, STORED))
        # The center of square 9 (row 1, col 1) is its 32x32 patch in the downscaled image
        np.testing.assert_array_equal(tiles[9, 4:36, 4:36], np.round(g[32:64, 32:64] * 255).astype(np.uint8))


class PiecesTests(unittest.TestCase):
    def test_app_shapes_parsed(self):
        shapes = pieces.app_shapes()
        self.assertEqual(set(shapes), set("pnbrqk"))
        for ch in "Pk":
            ink, paper = pieces.render_app_piece(ch, 40)
            self.assertEqual(ink.size, (40, 40))
            self.assertTrue(paper.getbbox())

    def test_relative_path(self):
        (pts, closed), = pieces.parse_path("M1 2h3v4H0z")
        self.assertTrue(closed)
        self.assertEqual(pts, [(1, 2), (4, 2), (4, 6), (0, 6)])


def _naive(meta, blob, x):
    a = x[:, None].astype(np.float64)
    for layer in meta["layers"]:
        if layer["type"] == "conv2d":
            k, p = layer["kernel"], layer["pad"]
            w = model_np._take(blob, layer["weight"]).reshape(layer["out"], layer["in"], k, k)
            b = model_np._take(blob, layer["bias"])
            n, c, h, ww = a.shape
            ap = np.pad(a, ((0, 0), (0, 0), (p, p), (p, p)))
            out = np.zeros((n, layer["out"], h, ww))
            for o in range(layer["out"]):
                for y in range(h):
                    for xx in range(ww):
                        out[:, o, y, xx] = (ap[:, :, y:y + k, xx:xx + k] * w[o]).sum(axis=(1, 2, 3)) + b[o]
            a = out
        elif layer["type"] == "maxpool2d":
            n, c, h, ww = a.shape
            a = a.reshape(n, c, h // 2, 2, ww // 2, 2).max(axis=(3, 5))
        elif layer["type"] == "flatten":
            a = a.reshape(a.shape[0], -1)
        else:
            w = model_np._take(blob, layer["weight"]).reshape(layer["out"], layer["in"])
            a = a @ w.T + model_np._take(blob, layer["bias"])
        if layer.get("relu"):
            a = np.maximum(a, 0)
    return a


class ModelFormatTests(unittest.TestCase):
    def test_forward_matches_naive_loops(self):
        rng = np.random.default_rng(1)
        layers, parts, off = [], [], 0

        def put(n):
            nonlocal off
            parts.append(rng.normal(0, 0.3, n).astype("<f4"))
            ref = [off, n]
            off += n
            return ref

        layers.append({"type": "conv2d", "in": 1, "out": 3, "kernel": 3, "pad": 1, "relu": True, "weight": put(27), "bias": put(3)})
        layers.append({"type": "maxpool2d", "size": 2})
        layers.append({"type": "flatten"})
        layers.append({"type": "dense", "in": 3 * 16 * 16, "out": 13, "relu": False, "weight": put(13 * 768), "bias": put(13)})
        blob = np.concatenate(parts)
        with tempfile.TemporaryDirectory() as tmp:
            meta = {"format": model_np.FORMAT, "format_version": model_np.FORMAT_VERSION, "layers": layers,
                    "weights_file": "m.bin", "weights_count": int(blob.size)}
            Path(tmp, "m.json").write_text(json.dumps(meta))
            blob.tofile(Path(tmp, "m.bin"))
            meta, blob = model_np.load(Path(tmp, "m.json"))
        x = rng.random((2, 32, 32)).astype(np.float32)
        np.testing.assert_allclose(model_np.forward(meta, blob, x), _naive(meta, blob, x), rtol=1e-4, atol=1e-4)


if __name__ == "__main__":
    unittest.main()
