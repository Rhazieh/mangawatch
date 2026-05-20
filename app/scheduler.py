from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import SessionLocal
from app.models.series import Series
from app.services.poller import poll_series

_scheduler = BackgroundScheduler()


def _run_mangadex_poll():
    db = SessionLocal()
    try:
        series_list = db.query(Series).filter(Series.source_type == "mangadex").all()
        for series in series_list:
            poll_series(series, db)
    finally:
        db.close()


def start():
    _scheduler.add_job(
        _run_mangadex_poll,
        "interval",
        seconds=settings.poll_interval_mangadex,
        id="mangadex_poll",
        replace_existing=True,
    )
    _scheduler.start()


def stop():
    _scheduler.shutdown(wait=False)
