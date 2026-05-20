from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.services.poller import poll_all

router = APIRouter(prefix="/internal", tags=["internal"])


def _check_poll_secret(authorization: str = Header(...)):
    if not settings.poll_secret:
        raise HTTPException(status_code=403, detail="Poll secret not configured")
    if authorization != f"Bearer {settings.poll_secret}":
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/poll")
def trigger_poll(
    db: Session = Depends(get_db),
    _: None = Depends(_check_poll_secret),
):
    return poll_all(db)
