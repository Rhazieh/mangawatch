"""Phase 5: mark-as-read, unsubscribe, Discord alerts, series title hydration."""
from unittest.mock import patch

from app.models.notification import Notification
from app.models.series import Series, Subscription
from app.models.user import User
from app.services.auth import hash_password
from tests.conftest import TestingSessionLocal
from tests.test_subscriptions import MANGADEX_URL, _auth_headers

MANWHACLAN_URL = "https://manhwaclan.com/manga/solo-leveling/"
KUNMANGA_URL = "https://kunmanga.com/manga/one-piece/"


def _seed_notification(client, read=False):
    """Register a user, create a series + notification, return (headers, notification_id)."""
    headers = _auth_headers(client)
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "u@example.com").first()
    series = Series(source_url=MANGADEX_URL, source_type="mangadex", external_id="abc")
    db.add(series)
    db.flush()
    n = Notification(user_id=user.id, series_id=series.id,
                     chapter_title="Ch 1", chapter_url="https://example.com", read=read)
    db.add(n)
    db.commit()
    nid = n.id
    db.close()
    return headers, nid


# ---------------------------------------------------------------------------
# Mark notification as read
# ---------------------------------------------------------------------------

def test_mark_notification_read(client):
    headers, nid = _seed_notification(client)
    r = client.patch(f"/notifications/{nid}/read", headers=headers)
    assert r.status_code == 200
    assert r.json()["read"] is True


def test_mark_notification_read_unknown_id(client):
    headers, _ = _seed_notification(client)
    r = client.patch("/notifications/99999/read", headers=headers)
    assert r.status_code == 404


def test_mark_notification_read_other_users_notification(client):
    _, nid = _seed_notification(client)

    # second user
    client.post("/auth/register", json={"email": "other@example.com", "password": "pass"})
    token = client.post(
        "/auth/login", json={"email": "other@example.com", "password": "pass"}
    ).json()["access_token"]
    other_headers = {"Authorization": f"Bearer {token}"}

    r = client.patch(f"/notifications/{nid}/read", headers=other_headers)
    assert r.status_code == 403


# ---------------------------------------------------------------------------
# Unsubscribe
# ---------------------------------------------------------------------------

def _seed_subscription(client):
    """Subscribe u@example.com to MANGADEX_URL, return (headers, series_id)."""
    headers = _auth_headers(client)
    client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)
    db = TestingSessionLocal()
    series_id = db.query(Series).filter(Series.source_url == MANGADEX_URL).first().id
    db.close()
    return headers, series_id


def test_unsubscribe(client):
    headers, series_id = _seed_subscription(client)
    r = client.delete(f"/subscriptions/{series_id}", headers=headers)
    assert r.status_code == 204

    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "u@example.com").first()
    count = db.query(Subscription).filter(
        Subscription.user_id == user.id,
        Subscription.series_id == series_id,
    ).count()
    db.close()
    assert count == 0


def test_unsubscribe_not_subscribed(client):
    headers = _auth_headers(client)
    r = client.delete("/subscriptions/99999", headers=headers)
    assert r.status_code == 404


# ---------------------------------------------------------------------------
# Discord webhook alerts
# ---------------------------------------------------------------------------

def test_discord_send_alert_posts_to_webhook(monkeypatch):
    from unittest.mock import MagicMock

    from app.services import discord

    monkeypatch.setattr(discord, "_WEBHOOK_URL", "https://discord.com/api/webhooks/test")
    mock_post = MagicMock()
    with patch("app.services.discord.httpx.post", mock_post):
        discord.send_alert("new chapter detected")

    mock_post.assert_called_once()
    payload = mock_post.call_args[1]["json"]
    assert "new chapter detected" in payload["content"]


def test_discord_send_alert_noop_when_url_not_set(monkeypatch):
    from unittest.mock import MagicMock

    from app.services import discord

    monkeypatch.setattr(discord, "_WEBHOOK_URL", "")
    mock_post = MagicMock()
    with patch("app.services.discord.httpx.post", mock_post):
        discord.send_alert("should not send")

    mock_post.assert_not_called()


def test_discord_send_alert_swallows_http_errors(monkeypatch):
    import httpx as _httpx

    from app.services import discord

    monkeypatch.setattr(discord, "_WEBHOOK_URL", "https://discord.com/api/webhooks/test")
    with patch("app.services.discord.httpx.post", side_effect=_httpx.ConnectError("down")):
        discord.send_alert("this should not raise")


def test_poller_alerts_on_new_chapter(client):
    from app.services.chapter import ChapterInfo
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    user = User(email="r@example.com", hashed_password=hash_password("x"))
    db.add(user)
    db.flush()
    series = Series(source_url=MANGADEX_URL, source_type="mangadex", external_id="abc")
    db.add(series)
    db.flush()
    db.add(Subscription(user_id=user.id, series_id=series.id))
    db.commit()

    chapter = ChapterInfo(id="ch-99", title="Ch 99", chapter_number="99",
                          url="https://mangadex.org/chapter/ch-99")
    with patch("app.services.poller.sources.get_latest_chapter", return_value=chapter), \
         patch("app.services.poller.discord.send_alert") as mock_alert:
        poll_series(series, db)

    db.close()
    mock_alert.assert_called_once()
    msg = mock_alert.call_args[0][0].lower()
    assert "ch-99" in msg or "chapter" in msg


def test_poller_alerts_on_poll_error(client):
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    series = Series(source_url=MANGADEX_URL, source_type="mangadex", external_id="abc")
    db.add(series)
    db.commit()

    with patch("app.services.poller.sources.get_latest_chapter", return_value=None), \
         patch("app.services.poller.discord.send_alert") as mock_alert:
        poll_series(series, db)

    db.close()
    mock_alert.assert_called_once()
    msg = mock_alert.call_args[0][0].lower()
    assert "error" in msg or "fail" in msg


# ---------------------------------------------------------------------------
# Series title hydration
# ---------------------------------------------------------------------------

_MANGADEX_TITLE_RESPONSE = {
    "data": {
        "attributes": {
            "title": {"en": "Solo Leveling"}
        }
    }
}


def test_mangadex_get_series_title_returns_title():
    from unittest.mock import MagicMock

    from app.services import mangadex

    mock_resp = MagicMock()
    mock_resp.json.return_value = _MANGADEX_TITLE_RESPONSE
    mock_resp.raise_for_status.return_value = None
    with patch("app.services.mangadex.httpx.get", return_value=mock_resp):
        title = mangadex.get_series_title(MANGADEX_URL)

    assert title == "Solo Leveling"


def test_subscribe_stores_series_title(client):
    headers = _auth_headers(client)
    with patch("app.routers.subscriptions.sources.get_series_title", return_value="Solo Leveling"):
        client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)

    db = TestingSessionLocal()
    series = db.query(Series).filter(Series.source_url == MANGADEX_URL).first()
    title = series.series_title
    db.close()
    assert title == "Solo Leveling"


def test_subscription_list_includes_series_title(client):
    headers = _auth_headers(client)
    with patch("app.routers.subscriptions.sources.get_series_title", return_value="Solo Leveling"):
        client.post("/subscriptions", json={"url": MANGADEX_URL}, headers=headers)

    r = client.get("/subscriptions", headers=headers)
    assert r.status_code == 200
    assert r.json()[0]["series_title"] == "Solo Leveling"


def test_notification_feed_includes_series_title(client):
    headers = _auth_headers(client)
    db = TestingSessionLocal()
    user = db.query(User).filter(User.email == "u@example.com").first()
    series = Series(source_url=MANGADEX_URL, source_type="mangadex",
                    external_id="abc", series_title="One Piece")
    db.add(series)
    db.flush()
    db.add(Notification(user_id=user.id, series_id=series.id,
                        chapter_title="Ch 1", chapter_url="https://example.com"))
    db.commit()
    db.close()

    r = client.get("/notifications", headers=headers)
    assert r.status_code == 200
    assert r.json()[0]["series_title"] == "One Piece"
