from unittest.mock import MagicMock, patch

import httpx

MANGADEX_URL = "https://mangadex.org/title/a1b2c3d4-e5f6-7890-abcd-ef1234567890"

_API_RESPONSE = {
    "data": [
        {
            "id": "chapter-uuid-001",
            "attributes": {
                "title": "The Final Battle",
                "chapter": "42",
                "translatedLanguage": "en",
            },
        }
    ]
}


def _mock_get(response_data):
    mock_resp = MagicMock()
    mock_resp.json.return_value = response_data
    mock_resp.raise_for_status.return_value = None
    return MagicMock(return_value=mock_resp)


def test_get_latest_chapter_returns_chapter_info(client):
    from app.services.mangadex import get_latest_chapter

    with patch("app.services.mangadex.httpx.get", _mock_get(_API_RESPONSE)):
        result = get_latest_chapter(MANGADEX_URL)

    assert result is not None
    assert result.id == "chapter-uuid-001"
    assert result.title == "The Final Battle"
    assert result.chapter_number == "42"
    assert "chapter-uuid-001" in result.url


def test_get_latest_chapter_returns_none_when_empty(client):
    from app.services.mangadex import get_latest_chapter

    with patch("app.services.mangadex.httpx.get", _mock_get({"data": []})):
        result = get_latest_chapter(MANGADEX_URL)

    assert result is None


def test_get_latest_chapter_returns_none_on_http_error(client):
    from app.services.mangadex import get_latest_chapter

    with patch("app.services.mangadex.httpx.get", side_effect=httpx.ConnectError("timeout")):
        result = get_latest_chapter(MANGADEX_URL)

    assert result is None


# --- poller ---

def _make_series_with_subscriber(db):
    """Helper: one Series with one subscribed User. Returns (series, user)."""
    from app.models.series import Series, Subscription
    from app.models.user import User
    from app.services.auth import hash_password

    user = User(email="reader@example.com", hashed_password=hash_password("x"))
    db.add(user)
    db.flush()

    series = Series(
        source_url=MANGADEX_URL,
        source_type="mangadex",
        external_id="a1b2c3d4-e5f6-7890-abcd-ef1234567890",
    )
    db.add(series)
    db.flush()

    db.add(Subscription(user_id=user.id, series_id=series.id))
    db.commit()
    return series, user


def test_poller_creates_notifications_for_subscribers(client):
    from app.models.notification import Notification
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    series, user = _make_series_with_subscriber(db)

    with patch("app.services.poller.sources.get_latest_chapter", return_value=_chapter_info()):
        poll_series(series, db)

    notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
    db.close()

    assert len(notifications) == 1
    assert notifications[0].chapter_title == "The Final Battle"


def _chapter_info():
    from app.services.chapter import ChapterInfo
    return ChapterInfo(id="chapter-uuid-001", title="The Final Battle", chapter_number="42",
                       url="https://mangadex.org/chapter/chapter-uuid-001")


def test_poller_does_nothing_when_source_returns_none(client):
    from app.models.notification import Notification
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    series, user = _make_series_with_subscriber(db)

    with patch("app.services.poller.sources.get_latest_chapter", return_value=None):
        result = poll_series(series, db)

    count = db.query(Notification).filter(Notification.user_id == user.id).count()
    db.close()
    assert result is False
    assert count == 0


def test_poller_skips_when_chapter_unchanged(client):
    from app.models.notification import Notification
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    series, user = _make_series_with_subscriber(db)
    series.last_chapter_id = "chapter-uuid-001"
    db.commit()

    with patch("app.services.poller.sources.get_latest_chapter", return_value=_chapter_info()):
        poll_series(series, db)

    count = db.query(Notification).filter(Notification.user_id == user.id).count()
    db.close()
    assert count == 0
