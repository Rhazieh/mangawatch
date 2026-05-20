from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.series import Series
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Notification, Series.series_title)
        .join(Series, Series.id == Notification.series_id)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        {
            "id": n.id,
            "series_id": n.series_id,
            "series_title": series_title,
            "chapter_title": n.chapter_title,
            "chapter_url": n.chapter_url,
            "read": n.read,
            "created_at": n.created_at,
        }
        for n, series_title in rows
    ]


@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    n = db.query(Notification).filter(Notification.id == notification_id).first()
    if not n:
        raise HTTPException(status_code=404, detail="Notification not found")
    if n.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Forbidden")
    n.read = True
    db.commit()
    return {"id": n.id, "read": n.read}
