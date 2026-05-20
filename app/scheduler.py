from apscheduler.schedulers.background import BackgroundScheduler

from app.config import settings
from app.database import SessionLocal
from app.models.series import Series
from app.services.poller import poll_series

_scheduler = BackgroundScheduler()


def _make_poll_job(source_type: str):
    def _run():
        db = SessionLocal()
        try:
            series_list = db.query(Series).filter(Series.source_type == source_type).all()
            for series in series_list:
                poll_series(series, db)
        finally:
            db.close()
    _run.__name__ = f"_run_{source_type}_poll"
    return _run


def start():
    _scheduler.add_job(
        _make_poll_job("mangadex"),
        "interval",
        seconds=settings.poll_interval_mangadex,
        id="mangadex_poll",
        replace_existing=True,
    )
    for source_type in ("manhwaclan", "kunmanga"):
        _scheduler.add_job(
            _make_poll_job(source_type),
            "interval",
            seconds=settings.poll_interval_scrape,
            id=f"{source_type}_poll",
            replace_existing=True,
        )
    _scheduler.start()


def stop():
    _scheduler.shutdown(wait=False)
