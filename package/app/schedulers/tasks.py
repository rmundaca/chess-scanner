import logging
from datetime import datetime, timedelta

from apscheduler.schedulers.background import BackgroundScheduler

from app.core.database import SessionLocal
from app.models.schemas import Scan
from app.services import scans as svc

logger = logging.getLogger("scheduler")
scheduler = BackgroundScheduler()


def cleanup_job():
    """Delete image folders with no scan in the DB and the stale export ZIP."""
    try:
        db = SessionLocal()
        try:
            ids = {str(i) for (i,) in db.query(Scan.id).all()}
        finally:
            db.close()
        removed = 0
        if svc.SCANS_DIR.exists():
            for folder in svc.SCANS_DIR.iterdir():
                if folder.is_dir() and folder.name.isdigit() and folder.name not in ids:
                    svc.delete_images(int(folder.name))
                    removed += 1
        if svc.EXPORT_PATH.exists():
            svc.EXPORT_PATH.unlink()
        if removed:
            logger.info("Cleanup: %d orphan folders removed.", removed)
    except Exception:
        logger.exception("Periodic cleanup failed.")


def start_scheduler():
    # Once a day, with a first run shortly after startup
    scheduler.add_job(cleanup_job, "interval", hours=24, id="cleanup", replace_existing=True,
                      next_run_time=datetime.now() + timedelta(minutes=5), max_instances=1, coalesce=True)
    scheduler.start()
    logger.info("APScheduler started.")


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
