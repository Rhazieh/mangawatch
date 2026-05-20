"""Phase 4: scrape-based sources, source dispatcher, scheduler wiring."""
from unittest.mock import patch

import httpx

from app.services.chapter import ChapterInfo

_MANGADEX_URL = "https://mangadex.org/title/a1b2c3d4-e5f6-7890-abcd-ef1234567890"
_MANWHACLAN_URL = "https://manhwaclan.com/manga/solo-leveling/"
_KUNMANGA_URL = "https://kunmanga.com/manga/one-piece/"

_CHAPTER = ChapterInfo(id="ch-1", title="The Beginning", chapter_number="1",
                       url="https://example.com/chapter/1")


# --- dispatcher ---

def test_dispatcher_routes_mangadex():
    from app.services import sources

    with patch("app.services.sources.mangadex.get_latest_chapter", return_value=_CHAPTER) as mock:
        result = sources.get_latest_chapter(_MANGADEX_URL, "mangadex")

    mock.assert_called_once_with(_MANGADEX_URL)
    assert result == _CHAPTER


def test_dispatcher_routes_manwhaclan():
    from app.services import sources

    with patch("app.services.sources.manhwaclan.get_latest_chapter", return_value=_CHAPTER) as mock:
        result = sources.get_latest_chapter(_MANWHACLAN_URL, "manhwaclan")

    mock.assert_called_once_with(_MANWHACLAN_URL)
    assert result == _CHAPTER


def test_dispatcher_routes_kunmanga():
    from app.services import sources

    with patch("app.services.sources.kunmanga.get_latest_chapter", return_value=_CHAPTER) as mock:
        result = sources.get_latest_chapter(_KUNMANGA_URL, "kunmanga")

    mock.assert_called_once_with(_KUNMANGA_URL)
    assert result == _CHAPTER


def test_dispatcher_returns_none_for_unknown_source():
    from app.services import sources

    result = sources.get_latest_chapter("https://unknown.com/manga/foo", "unknown")

    assert result is None


# --- ManwhaClan scraper ---

_MANWHACLAN_HTML = """
<html><body>
  <ul class="chapter-list">
    <li><a href="/manga/solo-leveling/chapter-200/">Chapter 200 - The Monarch's War</a></li>
    <li><a href="/manga/solo-leveling/chapter-199/">Chapter 199</a></li>
  </ul>
</body></html>
"""


def _mock_httpx_get(html: str):
    from unittest.mock import MagicMock
    mock_resp = MagicMock()
    mock_resp.text = html
    mock_resp.raise_for_status.return_value = None
    return MagicMock(return_value=mock_resp)


def test_manwhaclan_returns_chapter_info_from_html():
    from app.services import manhwaclan

    with patch("app.services.manhwaclan.httpx.get", _mock_httpx_get(_MANWHACLAN_HTML)):
        result = manhwaclan.get_latest_chapter(_MANWHACLAN_URL)

    assert result is not None
    assert result.chapter_number == "200"
    assert "chapter-200" in result.url
    assert result.id == "solo-leveling:200"


def test_manwhaclan_returns_none_when_no_chapters():
    from app.services import manhwaclan

    empty_html = "<html><body><ul class='chapter-list'></ul></body></html>"
    with patch("app.services.manhwaclan.httpx.get", _mock_httpx_get(empty_html)):
        result = manhwaclan.get_latest_chapter(_MANWHACLAN_URL)

    assert result is None


def test_manwhaclan_returns_none_on_http_error():
    from app.services import manhwaclan

    with patch("app.services.manhwaclan.httpx.get", side_effect=httpx.ConnectError("timeout")):
        result = manhwaclan.get_latest_chapter(_MANWHACLAN_URL)

    assert result is None


# --- KunManga scraper ---

_KUNMANGA_HTML = """
<html><body>
  <ul class="main version-chap no-volumn">
    <li class="wp-manga-chapter">
      <a href="https://kunmanga.com/manga/one-piece/chapter-1100/">Chapter 1100</a>
    </li>
    <li class="wp-manga-chapter">
      <a href="https://kunmanga.com/manga/one-piece/chapter-1099/">Chapter 1099</a>
    </li>
  </ul>
</body></html>
"""


def test_kunmanga_returns_chapter_info_from_html():
    from app.services import kunmanga

    with patch("app.services.kunmanga.httpx.get", _mock_httpx_get(_KUNMANGA_HTML)):
        result = kunmanga.get_latest_chapter(_KUNMANGA_URL)

    assert result is not None
    assert result.chapter_number == "1100"
    assert "chapter-1100" in result.url
    assert result.id == "one-piece:1100"


def test_kunmanga_returns_none_when_no_chapters():
    from app.services import kunmanga

    empty_html = "<html><body><ul class='main version-chap no-volumn'></ul></body></html>"
    with patch("app.services.kunmanga.httpx.get", _mock_httpx_get(empty_html)):
        result = kunmanga.get_latest_chapter(_KUNMANGA_URL)

    assert result is None


def test_kunmanga_returns_none_on_http_error():
    from app.services import kunmanga

    with patch("app.services.kunmanga.httpx.get", side_effect=httpx.ConnectError("timeout")):
        result = kunmanga.get_latest_chapter(_KUNMANGA_URL)

    assert result is None


# --- poller uses dispatcher ---

def test_poller_uses_dispatcher_not_mangadex_directly(client):
    """Poller should route through sources.get_latest_chapter, not import mangadex."""
    from app.models.notification import Notification
    from app.models.series import Series, Subscription
    from app.models.user import User
    from app.services.auth import hash_password
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal

    db = TestingSessionLocal()
    user = User(email="reader2@example.com", hashed_password=hash_password("x"))
    db.add(user)
    db.flush()
    series = Series(source_url=_MANWHACLAN_URL, source_type="manhwaclan",
                    external_id="solo-leveling")
    db.add(series)
    db.flush()
    db.add(Subscription(user_id=user.id, series_id=series.id))
    db.commit()

    chapter = ChapterInfo(id="solo-leveling:200", title=_CHAPTER.title,
                          chapter_number=_CHAPTER.chapter_number, url=_CHAPTER.url)
    with patch("app.services.poller.sources.get_latest_chapter", return_value=chapter):
        result = poll_series(series, db)

    notifications = db.query(Notification).filter(Notification.user_id == user.id).all()
    db.close()
    assert result is True
    assert len(notifications) == 1


# --- scheduler wiring ---

def test_scheduler_registers_scrape_jobs():
    from app import scheduler

    scheduler.start()
    job_ids = {job.id for job in scheduler._scheduler.get_jobs()}
    scheduler.stop()

    assert "manhwaclan_poll" in job_ids
    assert "kunmanga_poll" in job_ids
