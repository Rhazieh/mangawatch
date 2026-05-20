from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.metrics import new_chapters_total, poll_total
from app.models.notification import Notification
from app.models.series import Series, Subscription
from app.services.mangadex import get_latest_chapter


def poll_series(series: Series, db: Session) -> bool:
    """Poll one Series for a new chapter. Returns True if a new chapter was found."""
    latest = get_latest_chapter(series.source_url)
    if latest is None:
        poll_total.labels(source=series.source_type, status="error").inc()
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
    return True
