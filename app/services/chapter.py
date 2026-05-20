from dataclasses import dataclass


@dataclass
class ChapterInfo:
    id: str
    title: str | None
    chapter_number: str | None
    url: str
