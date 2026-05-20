from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.series import Series, Subscription
from app.models.user import User
from app.schemas.subscriptions import SubscribeRequest
from app.services import sources
from app.services.url_parser import parse_source_url

router = APIRouter(prefix="/subscriptions", tags=["subscriptions"])


@router.get("")
def list_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    rows = (
        db.query(Series)
        .join(Subscription, Subscription.series_id == Series.id)
        .filter(Subscription.user_id == current_user.id)
        .all()
    )
    return [{"id": s.id, "source_url": s.source_url, "source_type": s.source_type,
             "series_title": s.series_title} for s in rows]


@router.post("", status_code=201)
def subscribe(
    payload: SubscribeRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        source_type, external_id = parse_source_url(payload.url)
    except ValueError:
        raise HTTPException(status_code=400, detail="Unsupported source URL")

    series = db.query(Series).filter(Series.source_url == payload.url).first()
    if not series:
        series_title = sources.get_series_title(payload.url, source_type)
        series = Series(source_url=payload.url, source_type=source_type,
                        external_id=external_id, series_title=series_title)
        db.add(series)
        db.flush()

    if db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.series_id == series.id,
    ).first():
        raise HTTPException(status_code=409, detail="Already subscribed")

    db.add(Subscription(user_id=current_user.id, series_id=series.id))
    db.commit()
    return {"message": "Subscribed"}


@router.delete("/{series_id}", status_code=204)
def unsubscribe(
    series_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sub = db.query(Subscription).filter(
        Subscription.user_id == current_user.id,
        Subscription.series_id == series_id,
    ).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Subscription not found")
    db.delete(sub)
    db.commit()
