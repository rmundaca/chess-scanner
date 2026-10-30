"""Square recognition model (CNN trained on the PC, see training/README.md).

The package ships a bundled one in app/model/. One uploaded from Settings lives in data/models/
and takes precedence, so weights can be changed without repackaging the app.
"""
import hashlib
import json
import os
from pathlib import Path
from typing import Optional

from app.core.config import settings

BUNDLED_DIR = Path(__file__).resolve().parent.parent / "model"
MODELS_DIR = Path(settings["data_dir"]) / "models"
META_NAME = "model.json"
WEIGHTS_NAME = "model.bin"

FORMAT = "chess-scanner-cnn"
FORMAT_VERSION = 1
PREPROCESS_VERSION = 1
CLASSES = ["", "P", "N", "B", "R", "Q", "K", "p", "n", "b", "r", "q", "k"]
MAX_META_BYTES = 64 * 1024
MAX_WEIGHTS_BYTES = 8 * 1024 * 1024
_LAYER_TYPES = {"conv2d", "maxpool2d", "flatten", "dense"}


def active_dir() -> Optional[Path]:
    for folder in (MODELS_DIR, BUNDLED_DIR):
        if (folder / META_NAME).exists() and (folder / WEIGHTS_NAME).exists():
            return folder
    return None


def model_info() -> Optional[dict]:
    """Description of the active model (what vision.js needs), or None if there is none."""
    folder = active_dir()
    if not folder:
        return None
    meta = json.loads((folder / META_NAME).read_text(encoding="utf-8"))
    meta["id"] = meta["sha256"][:12]
    meta["source"] = "uploaded" if folder == MODELS_DIR else "bundled"
    meta.pop("weights_file", None)
    return meta


def weights_path() -> Optional[Path]:
    folder = active_dir()
    return folder / WEIGHTS_NAME if folder else None


def validate(meta_raw: bytes, weights: bytes) -> dict:
    """Check that the json/bin pair is a model vision.js can run. Raises ValueError("invalid_model")."""
    try:
        if len(meta_raw) > MAX_META_BYTES or len(weights) > MAX_WEIGHTS_BYTES:
            raise ValueError
        meta = json.loads(meta_raw.decode("utf-8"))
        count = int(meta["weights_count"])
        ok = (
            meta.get("format") == FORMAT
            and meta.get("format_version") == FORMAT_VERSION
            and meta.get("preprocess_version") == PREPROCESS_VERSION
            and meta.get("classes") == CLASSES
            and meta.get("input") == [1, 32, 32]
            and len(weights) == count * 4
            and hashlib.sha256(weights).hexdigest() == meta.get("sha256")
        )
        if not ok or not meta.get("layers"):
            raise ValueError
        for layer in meta["layers"]:
            if layer.get("type") not in _LAYER_TYPES:
                raise ValueError
            for key in ("weight", "bias"):
                if key in layer:
                    off, n = (int(v) for v in layer[key])
                    if off < 0 or n <= 0 or off + n > count:
                        raise ValueError
        last = meta["layers"][-1]
        if last.get("type") != "dense" or last.get("out") != len(CLASSES):
            raise ValueError
    except (ValueError, KeyError, TypeError, UnicodeDecodeError):
        raise ValueError("invalid_model")
    return meta


def install(meta_raw: bytes, weights: bytes) -> None:
    meta = validate(meta_raw, weights)
    meta["weights_file"] = WEIGHTS_NAME
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    # The json is what activates the model: removed first and written last
    (MODELS_DIR / META_NAME).unlink(missing_ok=True)
    for name, data in ((WEIGHTS_NAME, weights), (META_NAME, json.dumps(meta, indent=1).encode("utf-8"))):
        tmp = MODELS_DIR / (name + ".tmp")
        tmp.write_bytes(data)
        os.replace(tmp, MODELS_DIR / name)


def reset() -> None:
    for name in (META_NAME, WEIGHTS_NAME):
        (MODELS_DIR / name).unlink(missing_ok=True)
