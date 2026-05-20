import httpx

from app.services.chapter import ChapterInfo
from app.services.url_parser import parse_source_url

_API_BASE = "https://api.mangadex.org"


def get_latest_chapter(series_url: str) -> ChapterInfo | None:
    try:
        _, manga_id = parse_source_url(series_url)
        resp = httpx.get(
            f"{_API_BASE}/manga/{manga_id}/feed",
            params={
                "limit": 1,
                "order[chapter]": "desc",
                "translatedLanguage[]": "en",
            },
            timeout=10,
        )
        resp.raise_for_status()
        data = resp.json()
        if not data["data"]:
            return None
        chapter = data["data"][0]
        attrs = chapter["attributes"]
        return ChapterInfo(
            id=chapter["id"],
            title=attrs.get("title"),
            chapter_number=attrs.get("chapter"),
            url=f"https://mangadex.org/chapter/{chapter['id']}",
        )
    except Exception:
        return None
