import base64
import hashlib
import io
import json
import struct
import unittest
import zipfile

from fastapi.testclient import TestClient

from app.main import app
from app.services import model as model_svc
from app.services import scans as svc

START = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"
FAKE_JPEG = "data:image/jpeg;base64," + base64.b64encode(b"\xff\xd8\xff\xe0" + b"0" * 64).decode()


def scan_payload(**overrides):
    body = {
        "title": "  Book, diagram 12  ",
        "placement": START,
        "side": "b",
        "castling": "KQkq",
        "flipped": True,
        "corners": [[0.1, 0.1], [0.9, 0.12], [0.88, 0.9], [0.12, 0.88]],
        "board_image": FAKE_JPEG,
        "photo_image": FAKE_JPEG,
    }
    body.update(overrides)
    return body


class HealthTest(unittest.TestCase):
    def test_health(self):
        res = TestClient(app).get("/api/health")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "ok")


class ScansApiTest(unittest.TestCase):
    def setUp(self):
        # No "with": startup events don't fire (the scheduler doesn't run in tests)
        self.client = TestClient(app)

    def create(self, **overrides):
        res = self.client.post("/api/scans", json=scan_payload(**overrides))
        self.assertEqual(res.status_code, 200, res.text)
        return res.json()

    def test_create_list_images_delete(self):
        scan = self.create()
        self.assertEqual(scan["title"], "Book, diagram 12")
        self.assertEqual(scan["fen"], START + " b KQkq - 0 1")
        self.assertTrue(scan["flipped"])
        self.assertTrue(scan["has_photo"])
        self.assertIn(scan["id"], [s["id"] for s in self.client.get("/api/scans").json()])

        board = self.client.get(f"/api/scans/{scan['id']}/board.jpg")
        self.assertEqual(board.status_code, 200)
        self.assertTrue(board.content.startswith(b"\xff\xd8\xff"))
        self.assertEqual(self.client.get(f"/api/scans/{scan['id']}/other.jpg").status_code, 404)

        self.assertEqual(self.client.delete(f"/api/scans/{scan['id']}").status_code, 200)
        self.assertFalse(svc.scan_dir(scan["id"]).exists())
        self.assertEqual(self.client.delete(f"/api/scans/{scan['id']}").json()["detail"], "not_found")
        self.assertEqual(self.client.get(f"/api/scans/{scan['id']}/board.jpg").status_code, 404)

    def test_photo_is_optional(self):
        scan = self.create(photo_image=None, corners=None, title="")
        self.assertFalse(scan["has_photo"])
        self.assertIsNone(scan["title"])
        self.assertEqual(self.client.get(f"/api/scans/{scan['id']}/photo.jpg").status_code, 404)

    def test_update_position(self):
        scan = self.create()
        res = self.client.put(f"/api/scans/{scan['id']}", json={
            "title": "Corrected", "placement": "4k3/8/8/8/8/8/8/4K3", "side": "w", "castling": "", "flipped": False})
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["fen"], "4k3/8/8/8/8/8/8/4K3 w - - 0 1")
        self.assertEqual(res.json()["title"], "Corrected")

    def test_rejects_invalid_positions(self):
        bad = [
            {"placement": "8/8/8"},
            {"placement": "9/8/8/8/8/8/8/8"},
            {"placement": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNX"},
            {"placement": "rnbqkbnr/ppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR"},
            {"side": "x"},
            {"castling": "QK"},
        ]
        for override in bad:
            res = self.client.post("/api/scans", json=scan_payload(**override))
            self.assertEqual(res.status_code, 400, override)
            self.assertEqual(res.json()["detail"], "invalid_fen", override)

    def test_rejects_invalid_images_and_corners(self):
        cases = [
            ({"board_image": "data:image/png;base64,AAAA"}, "invalid_image"),
            ({"board_image": "data:image/jpeg;base64,!!!"}, "invalid_image"),
            ({"board_image": "data:image/jpeg;base64," + base64.b64encode(b"GIF89a").decode()}, "invalid_image"),
            ({"board_image": "data:image/jpeg;base64," + "A" * (2 * 1024 * 1024)}, "image_too_large"),
            ({"corners": [[0, 0], [1, 0], [1, 1]]}, "invalid_corners"),
            ({"corners": [[0, 0], [1, 0], [1, 1], [0, 1.5]]}, "invalid_corners"),
        ]
        for override, code in cases:
            res = self.client.post("/api/scans", json=scan_payload(**override))
            self.assertEqual(res.status_code, 400, override)
            self.assertEqual(res.json()["detail"], code)

    def test_export_zip(self):
        scan = self.create()
        res = self.client.get("/api/scans/export")
        self.assertEqual(res.status_code, 200)
        with zipfile.ZipFile(io.BytesIO(res.content)) as zf:
            labels = json.loads(zf.read("labels.json"))
            entry = next(item for item in labels if item["id"] == scan["id"])
            self.assertEqual(entry["placement"], START)
            self.assertEqual(len(entry["corners"]), 4)
            self.assertIn(entry["files"]["board"], zf.namelist())
            self.assertIsNone(entry["predicted"])

    def test_prediction_is_stored(self):
        predicted = "rnbqkbnr" + "p" * 8 + "." * 32 + "P" * 8 + "RNBQKBNR"
        scan = self.create(predicted=predicted, model_id="0123abcd")
        self.assertEqual(scan["predicted"], predicted)
        self.assertEqual(scan["model_id"], "0123abcd")
        for override in ({"predicted": "x" * 64, "model_id": "ab"}, {"predicted": "." * 63, "model_id": "ab"},
                         {"predicted": "." * 64, "model_id": None}, {"predicted": "." * 64, "model_id": "../x"}):
            res = self.client.post("/api/scans", json=scan_payload(**override))
            self.assertEqual(res.status_code, 400, override)
            self.assertEqual(res.json()["detail"], "invalid_prediction")


def tiny_model(**meta_overrides):
    """Minimal model in the training/model_np.py format: conv 1->1, pool 32, flatten, dense 1->13."""
    count = 9 + 1 + 13 + 13
    weights = struct.pack(f"<{count}f", *([0.1] * count))
    meta = {
        "format": "chess-scanner-cnn", "format_version": 1, "preprocess_version": 1,
        "created": "2026-10-16T00:00:00Z", "input": [1, 32, 32], "classes": model_svc.CLASSES,
        "weights_file": "model.bin", "weights_count": count, "sha256": hashlib.sha256(weights).hexdigest(),
        "layers": [
            {"type": "conv2d", "in": 1, "out": 1, "kernel": 3, "pad": 1, "relu": True, "weight": [0, 9], "bias": [9, 1]},
            {"type": "maxpool2d", "size": 32},
            {"type": "flatten"},
            {"type": "dense", "in": 1, "out": 13, "relu": False, "weight": [10, 13], "bias": [23, 13]},
        ],
        "metrics": {"real_val_acc": 0.99},
    }
    meta.update(meta_overrides)
    return json.dumps(meta).encode(), weights


class ModelApiTest(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.addCleanup(model_svc.reset)

    def upload(self, meta, weights):
        return self.client.post("/api/model", files={"meta": ("model.json", meta), "weights": ("model.bin", weights)})

    def test_bundled_model_is_served(self):
        info = self.client.get("/api/model").json()
        self.assertEqual(info["source"], "bundled")
        self.assertEqual(info["classes"], model_svc.CLASSES)
        res = self.client.get(f"/api/model/weights?v={info['id']}")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(res.content), info["weights_count"] * 4)
        self.assertNotIn("weights_file", info)

    def test_upload_and_reset(self):
        meta, weights = tiny_model()
        res = self.upload(meta, weights)
        self.assertEqual(res.status_code, 200, res.text)
        self.assertEqual(res.json()["source"], "uploaded")
        self.assertEqual(self.client.get("/api/model/weights").content, weights)
        res = self.client.delete("/api/model")
        self.assertEqual(res.json()["source"], "bundled")

    def test_rejects_invalid_models(self):
        meta, weights = tiny_model()
        bad = [
            (meta, weights[:-4]),
            (meta, weights[:-4] + bytes(4)),
            (tiny_model(format_version=2)[0], weights),
            (tiny_model(preprocess_version=2)[0], weights),
            (tiny_model(classes=["", "P"])[0], weights),
            (tiny_model(layers=[{"type": "lstm"}])[0], weights),
            (tiny_model(layers=[{"type": "dense", "in": 1, "out": 13, "weight": [30, 13], "bias": [0, 13]}])[0], weights),
            (b"no json", weights),
        ]
        for m, w in bad:
            res = self.upload(m, w)
            self.assertEqual(res.status_code, 400)
            self.assertEqual(res.json()["detail"], "invalid_model")
        self.assertEqual(self.client.get("/api/model").json()["source"], "bundled")


class FenHelpersTest(unittest.TestCase):
    def test_valid_placement(self):
        self.assertTrue(svc.valid_placement(START))
        self.assertTrue(svc.valid_placement("8/8/8/8/8/8/8/8"))
        self.assertFalse(svc.valid_placement("8/8/8/8/8/8/8/8/8"))
        self.assertFalse(svc.valid_placement("44/8/8/8/8/8/8/71"))

    def test_clean_position_defaults_castling(self):
        self.assertEqual(svc.clean_position(START, "w", ""), (START, "w", "-"))


if __name__ == "__main__":
    unittest.main()
