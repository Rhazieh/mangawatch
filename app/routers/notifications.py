from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.notification import Notification
from app.models.user import User

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.get("")
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .all()
    )
    return [
        {
            "id": n.id,
            "series_id": n.series_id,
            "chapter_title": n.chapter_title,
            "chapter_url": n.chapter_url,
            "read": n.read,
            "created_at": n.created_at,
        }
        for n in rows
    ]
