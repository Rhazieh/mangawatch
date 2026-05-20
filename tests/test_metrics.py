def test_metrics_endpoint_returns_200(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert "mangawatch" in r.text


def test_poll_counter_increments_after_successful_poll(client):
    from unittest.mock import patch

    from app.metrics import poll_total
    from app.services.chapter import ChapterInfo
    from app.services.poller import poll_series
    from tests.conftest import TestingSessionLocal
    from tests.test_poller import _make_series_with_subscriber

    db = TestingSessionLocal()
    series, _ = _make_series_with_subscriber(db)

    before = poll_total.labels(source="mangadex", status="success")._value.get()

    chapter = ChapterInfo(id="c1", title="Ch 1", chapter_number="1",
                          url="https://mangadex.org/chapter/c1")
    with patch("app.services.poller.sources.get_latest_chapter", return_value=chapter):
        poll_series(series, db)

    db.close()
    after = poll_total.labels(source="mangadex", status="success")._value.get()
    assert after == before + 1
