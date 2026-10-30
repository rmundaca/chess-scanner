import base64
import binascii
import re
import shutil
from pathlib import Path
from typing import List, Optional

from app.core.config import settings

SCANS_DIR = Path(settings["data_dir"]) / "scans"
EXPORT_PATH = Path(settings["data_dir"]) / "export.zip"

PIECES = set("PNBRQKpnbrqk")
_CASTLING_RE = re.compile(r"^(-|K?Q?k?q?)$")
_PREDICTED_RE = re.compile(r"^[.PNBRQKpnbrqk]{64}$")
_MODEL_ID_RE = re.compile(r"^[0-9a-f]{1,16}$")
_DATA_URL_PREFIX = "data:image/jpeg;base64,"
_JPEG_MAGIC = b"\xff\xd8\xff"

MAX_BOARD_BYTES = 1 * 1024 * 1024
MAX_PHOTO_BYTES = 4 * 1024 * 1024


def valid_placement(placement: str) -> bool:
    """First FEN field: 8 ranks separated by '/', each adding up to 8 squares."""
    ranks = placement.split("/")
    if len(ranks) != 8:
        return False
    for rank in ranks:
        squares = 0
        prev_digit = False
        for ch in rank:
            if ch in PIECES:
                squares += 1
                prev_digit = False
            elif ch in "12345678" and not prev_digit:  # canonical FEN: never two digits in a row
                squares += int(ch)
                prev_digit = True
            else:
                return False
        if squares != 8:
            return False
    return True


def clean_position(placement: str, side: str, castling: str) -> tuple:
    """Validate and normalize the position. Raises ValueError("invalid_fen")."""
    placement = (placement or "").strip()
    castling = (castling or "").strip() or "-"
    if not valid_placement(placement) or side not in ("w", "b") or not _CASTLING_RE.match(castling):
        raise ValueError("invalid_fen")
    return placement, side, castling


def clean_corners(corners: Optional[List[List[float]]]) -> Optional[List[List[float]]]:
    """Corners normalized (0..1) to the photo: [[x, y]] x4. Raises ValueError("invalid_corners")."""
    if corners is None:
        return None
    if len(corners) != 4 or any(len(p) != 2 or not all(0.0 <= v <= 1.0 for v in p) for p in corners):
        raise ValueError("invalid_corners")
    return [[round(float(x), 5), round(float(y), 5)] for x, y in corners]


def clean_prediction(predicted: Optional[str], model_id: Optional[str]) -> tuple:
    """Model proposal as seen (64 squares, '.' = empty). Raises ValueError("invalid_prediction")."""
    if predicted is None:
        return None, None
    if not _PREDICTED_RE.match(predicted) or not _MODEL_ID_RE.match(model_id or ""):
        raise ValueError("invalid_prediction")
    return predicted, model_id


def build_fen(placement: str, side: str, castling: str) -> str:
    return f"{placement} {side} {castling} - 0 1"


def decode_jpeg(data_url: Optional[str], max_bytes: int) -> bytes:
    """JPEG data URL -> bytes. Raises ValueError("invalid_image" | "image_too_large")."""
    if not data_url or not data_url.startswith(_DATA_URL_PREFIX):
        raise ValueError("invalid_image")
    payload = data_url[len(_DATA_URL_PREFIX):]
    if len(payload) > max_bytes * 4 // 3 + 4:
        raise ValueError("image_too_large")
    try:
        raw = base64.b64decode(payload, validate=True)
    except (binascii.Error, ValueError):
        raise ValueError("invalid_image")
    if not raw.startswith(_JPEG_MAGIC):
        raise ValueError("invalid_image")
    return raw


def scan_dir(scan_id: int) -> Path:
    return SCANS_DIR / str(scan_id)


def save_images(scan_id: int, board: bytes, photo: Optional[bytes]) -> None:
    folder = scan_dir(scan_id)
    folder.mkdir(parents=True, exist_ok=True)
    (folder / "board.jpg").write_bytes(board)
    if photo:
        (folder / "photo.jpg").write_bytes(photo)


def delete_images(scan_id: int) -> None:
    shutil.rmtree(scan_dir(scan_id), ignore_errors=True)
