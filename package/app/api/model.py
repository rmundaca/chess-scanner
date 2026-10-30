from fastapi import APIRouter, File, HTTPException, UploadFile
from fastapi.responses import FileResponse

from app.services import model as svc

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("")
def get_model():
    info = svc.model_info()
    if not info:
        raise HTTPException(status_code=404, detail="model_missing")
    return info


@router.get("/weights")
def get_weights():
    path = svc.weights_path()
    if not path:
        raise HTTPException(status_code=404, detail="model_missing")
    # The client requests ?v=<id>: a given URL's content never changes
    return FileResponse(path, media_type="application/octet-stream",
                        headers={"Cache-Control": "private, max-age=31536000, immutable"})


@router.post("")
async def upload_model(meta: UploadFile = File(...), weights: UploadFile = File(...)):
    meta_raw = await meta.read(svc.MAX_META_BYTES + 1)
    weights_raw = await weights.read(svc.MAX_WEIGHTS_BYTES + 1)
    try:
        svc.install(meta_raw, weights_raw)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except OSError:
        raise HTTPException(status_code=500, detail="storage_error")
    return svc.model_info()


@router.delete("")
def reset_model():
    """Revert to the bundled model."""
    try:
        svc.reset()
    except OSError:
        raise HTTPException(status_code=500, detail="storage_error")
    info = svc.model_info()
    if not info:
        raise HTTPException(status_code=404, detail="model_missing")
    return info
