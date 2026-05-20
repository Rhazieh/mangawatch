import httpx
from bs4 import BeautifulSoup

from app.services.chapter import ChapterInfo
from app.services.url_parser import parse_source_url


def get_latest_chapter(series_url: str) -> ChapterInfo | None:
    try:
        resp = httpx.get(series_url, timeout=10, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        return _parse(series_url, resp.text)
    except Exception:
        return None


def _parse(series_url: str, html: str) -> ChapterInfo | None:
    soup = BeautifulSoup(html, "html.parser")
    items = soup.select("ul.main.version-chap li.wp-manga-chapter a")
    if not items:
        return None
    first = items[0]
    url = first.get("href", "")
    _, external_id = parse_source_url(series_url)
    chapter_number = _extract_chapter_number(url)
    return ChapterInfo(
        id=f"{external_id}:{chapter_number}",
        title=first.get_text(strip=True),
        chapter_number=chapter_number,
        url=url,
    )


def get_series_title(series_url: str) -> str | None:
    try:
        resp = httpx.get(series_url, timeout=10, follow_redirects=True,
                         headers={"User-Agent": "Mozilla/5.0"})
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.select_one("h1.post-title") or soup.find("h1")
        return tag.get_text(strip=True) if tag else None
    except Exception:
        return None


def _extract_chapter_number(href: str) -> str | None:
    import re
    m = re.search(r"chapter-(\d+(?:\.\d+)?)", href)
    return m.group(1) if m else None
