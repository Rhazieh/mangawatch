from fastapi import FastAPI

import app.models.notification  # noqa: F401
import app.models.series  # noqa: F401 — registers models with Base
from app.routers import auth, notifications, subscriptions

app = FastAPI(title="MangaWatch", version="0.1.0")

app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)


@app.get("/")
def root():
    return {"app": "MangaWatch", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
