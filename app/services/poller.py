from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.metrics import new_chapters_total, poll_total
from app.models.notification import Notification
from app.models.series import Series, Subscription
from app.services import discord, sources


def poll_all(db: Session) -> dict[str, int]:
    """Poll every tracked series. Returns a summary of the run."""
    series_list = db.query(Series).all()
    new = sum(1 for series in series_list if poll_series(series, db))
    return {"series_checked": len(series_list), "new_chapters": new}


def poll_series(series: Series, db: Session) -> bool:
    """Poll one Series for a new chapter. Returns True if a new chapter was found."""
    latest = sources.get_latest_chapter(series.source_url, series.source_type)
    if latest is None:
        poll_total.labels(source=series.source_type, status="error").inc()
        discord.send_alert(f"[{series.source_type}] poll error for {series.source_url}")
        return False
    if latest.id == series.last_chapter_id:
        poll_total.labels(source=series.source_type, status="success").inc()
        return False

    subscriptions = db.query(Subscription).filter(Subscription.series_id == series.id).all()
    for sub in subscriptions:
        db.add(Notification(
            user_id=sub.user_id,
            series_id=series.id,
            chapter_title=latest.title or f"Chapter {latest.chapter_number}",
            chapter_url=latest.url,
        ))

    series.last_chapter_id = latest.id
    series.last_chapter_title = latest.title
    series.last_chapter_url = latest.url
    series.last_polled_at = datetime.now(timezone.utc)
    db.commit()

    poll_total.labels(source=series.source_type, status="success").inc()
    new_chapters_total.labels(source=series.source_type).inc()
    label = latest.title or latest.chapter_number
    discord.send_alert(f"[{series.source_type}] new chapter: {label} — {latest.url}")
    return True
