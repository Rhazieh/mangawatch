from prometheus_client import Counter

poll_total = Counter(
    "mangawatch_poll_total",
    "Number of poll attempts",
    ["source", "status"],
)

new_chapters_total = Counter(
    "mangawatch_new_chapters_total",
    "Number of new chapters detected",
    ["source"],
)

# Pre-initialize known label combinations so they appear at 0 before the first poll
for _source in ("mangadex", "manwhaclan", "kunmanga"):
    poll_total.labels(source=_source, status="success")
    poll_total.labels(source=_source, status="error")
    new_chapters_total.labels(source=_source)
