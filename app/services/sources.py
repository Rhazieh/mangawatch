from app.services import kunmanga, mangadex, manwhaclan
from app.services.chapter import ChapterInfo
from app.services.url_parser import parse_source_url

__all__ = ["parse_source_url", "get_latest_chapter"]

_MODULES: dict = {
    "mangadex": mangadex,
    "manwhaclan": manwhaclan,
    "kunmanga": kunmanga,
}


def get_latest_chapter(source_url: str, source_type: str) -> ChapterInfo | None:
    module = _MODULES.get(source_type)
    if module is None:
        return None
    return module.get_latest_chapter(source_url)
