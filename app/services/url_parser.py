import re

_PATTERNS = {
    "mangadex": re.compile(r"mangadex\.org/title/([a-f0-9-]{36})"),
    "manhwaclan": re.compile(r"manhwaclan\.com/manga/([^/?#]+)"),
    "kunmanga": re.compile(r"kunmanga\.com/manga/([^/?#]+)"),
}


def parse_source_url(url: str) -> tuple[str, str]:
    """Return (source_type, external_id) or raise ValueError for unsupported URLs."""
    for source_type, pattern in _PATTERNS.items():
        if m := pattern.search(url):
            return source_type, m.group(1)
    raise ValueError(f"Unsupported source URL: {url}")
