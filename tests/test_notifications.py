from datetime import datetime, timedelta, timezone

from app.models.notification import Notification
from app.models.user import User
from tests.conftest import TestingSessionLocal
from tests.test_subscriptions import MANGADEX_URL, _auth_headers


def test_notifications_empty_for_new_user(client):
    r = client.get("/notifications", headers=_auth_headers(client))
    assert r.status_code == 200
    assert r.json() == []


def test_notifications_returned_newest_first(client):
    headers = _auth_headers(client)

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "u@example.com").first()

    from app.models.series import Series
    series = Series(source_url=MANGADEX_URL, source_type="mangadex", external_id="abc")
    db.add(series)
    db.flush()

    now = datetime.now(timezone.utc)
    db.add(Notification(
        user_id=user.id, series_id=series.id, chapter_title="Chapter 1",
        created_at=now - timedelta(hours=2),
    ))
    db.add(Notification(
        user_id=user.id, series_id=series.id, chapter_title="Chapter 2",
        created_at=now,
    ))
    db.commit()
    db.close()

    r = client.get("/notifications", headers=headers)
    assert r.status_code == 200
    titles = [n["chapter_title"] for n in r.json()]
    assert titles == ["Chapter 2", "Chapter 1"]
