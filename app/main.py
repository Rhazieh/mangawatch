from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

import app.metrics  # noqa: F401 — registers Prometheus counters
import app.models.notification  # noqa: F401
import app.models.series  # noqa: F401 — registers models with Base
from app import scheduler
from app.routers import auth, internal, metrics, notifications, subscriptions


@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.start()
    yield
    scheduler.stop()


app = FastAPI(title="MangaWatch", version="0.1.0", lifespan=lifespan)

app.include_router(auth.router)
app.include_router(subscriptions.router)
app.include_router(notifications.router)
app.include_router(metrics.router)
app.include_router(internal.router)

app.mount("/ui", StaticFiles(directory="frontend", html=True), name="ui")


@app.get("/")
def root():
    return RedirectResponse(url="/ui/login.html")


@app.get("/health")
def health():
    return {"status": "ok"}
