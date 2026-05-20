import httpx

from app.config import settings

_WEBHOOK_URL: str = settings.discord_webhook_url


def send_alert(message: str) -> None:
    if not _WEBHOOK_URL:
        return
    try:
        httpx.post(_WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception:
        pass
