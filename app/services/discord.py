import os

import httpx

_WEBHOOK_URL: str = os.getenv("DISCORD_WEBHOOK_URL", "")


def send_alert(message: str) -> None:
    if not _WEBHOOK_URL:
        return
    try:
        httpx.post(_WEBHOOK_URL, json={"content": message}, timeout=5)
    except Exception:
        pass
