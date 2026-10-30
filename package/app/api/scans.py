import json
import zipfile
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.schemas import Scan
from app.services import scans as svc

router = APIRouter(prefix="/api/scans", tags=["scans"])


class PositionIn(BaseModel):
    title: Optional[str] = None
    placement: str
    side: str = "w"
    castling: str = "-"
    flipped: bool = False


class ScanIn(PositionIn):
    corners: Optional[List[List[float]]] = None
    board_image: str  # JPEG data URL of the rectified (square) board
    photo_image: Optional[str] = None  # JPEG data URL of the downscaled original photo
    predicted: Optional[str] = None  # model proposal (visual order, "." = empty)
    model_id: Optional[str] = None


def _iso(dt) -> str:
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def scan_view(scan: Scan) -> dict:
    return {
        "id": scan.id,
        "title": scan.title,
        "placement": scan.placement,
        "side": scan.side,
        "castling": scan.castling,
        "flipped": scan.flipped,
        "fen": svc.build_fen(scan.placement, scan.side, scan.castling),
        "has_photo": scan.has_photo,
        "predicted": scan.predicted,
        "model_id": scan.model_id,
        "created_at": _iso(scan.created_at),
        "updated_at": _iso(scan.updated_at),
    }


def _get_scan(db: Session, scan_id: int) -> Scan:
    scan = db.get(Scan, scan_id)
    if not scan:
        raise HTTPException(status_code=404, detail="not_found")
    return scan


def _apply_position(scan: Scan, req: PositionIn) -> None:
    try:
        scan.placement, scan.side, scan.castling = svc.clean_position(req.placement, req.side, req.castling)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    scan.flipped = req.flipped
    scan.title = (req.title or "").strip()[:120] or None


@router.get("")
def list_scans(db: Session = Depends(get_db)):
    scans = db.query(Scan).order_by(Scan.created_at.desc(), Scan.id.desc()).all()
    return [scan_view(s) for s in scans]


@router.get("/export")
def export_scans(db: Session = Depends(get_db)):
    """ZIP with images and labels, for training the model on the PC."""
    scans = db.query(Scan).order_by(Scan.id).all()
    labels = []
    with zipfile.ZipFile(svc.EXPORT_PATH, "w", zipfile.ZIP_STORED) as zf:  # JPEGs are already compressed
        for s in scans:
            folder = svc.scan_dir(s.id)
            files = {}
            for name in ("board.jpg", "photo.jpg"):
                if (folder / name).exists():
                    arcname = f"scans/{s.id}/{name}"
                    zf.write(folder / name, arcname)
                    files[name.split(".")[0]] = arcname
            labels.append({**scan_view(s), "corners": json.loads(s.corners) if s.corners else None, "files": files})
        zf.writestr("labels.json", json.dumps(labels, ensure_ascii=False, indent=1))
    return FileResponse(svc.EXPORT_PATH, media_type="application/zip", filename="chess-scanner-dataset.zip",
                        headers={"Cache-Control": "no-store"})


@router.post("")
def create_scan(req: ScanIn, db: Session = Depends(get_db)):
    scan = Scan()
    _apply_position(scan, req)
    try:
        corners = svc.clean_corners(req.corners)
        scan.predicted, scan.model_id = svc.clean_prediction(req.predicted, req.model_id)
        board = svc.decode_jpeg(req.board_image, svc.MAX_BOARD_BYTES)
        photo = svc.decode_jpeg(req.photo_image, svc.MAX_PHOTO_BYTES) if req.photo_image else None
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    scan.corners = json.dumps(corners) if corners else None
    scan.has_photo = photo is not None
    db.add(scan)
    db.commit()
    db.refresh(scan)
    try:
        svc.save_images(scan.id, board, photo)
    except OSError:
        db.delete(scan)
        db.commit()
        svc.delete_images(scan.id)
        raise HTTPException(status_code=500, detail="storage_error")
    return scan_view(scan)


@router.put("/{scan_id}")
def update_scan(scan_id: int, req: PositionIn, db: Session = Depends(get_db)):
    scan = _get_scan(db, scan_id)
    _apply_position(scan, req)
    db.commit()
    db.refresh(scan)
    return scan_view(scan)


@router.delete("/{scan_id}")
def delete_scan(scan_id: int, db: Session = Depends(get_db)):
    scan = _get_scan(db, scan_id)
    db.delete(scan)
    db.commit()
    svc.delete_images(scan_id)
    return {"status": "deleted"}


@router.get("/{scan_id}/{name}.jpg")
def scan_image(scan_id: int, name: str, db: Session = Depends(get_db)):
    if name not in ("board", "photo"):
        raise HTTPException(status_code=404, detail="not_found")
    _get_scan(db, scan_id)
    path = svc.scan_dir(scan_id) / f"{name}.jpg"
    if not path.exists():
        raise HTTPException(status_code=404, detail="not_found")
    # Images never change for a given id
    return FileResponse(path, media_type="image/jpeg", headers={"Cache-Control": "private, max-age=31536000, immutable"})
