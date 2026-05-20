from fastapi import FastAPI

from app.routers import auth

app = FastAPI(title="MangaWatch", version="0.1.0")

app.include_router(auth.router)


@app.get("/")
def root():
    return {"app": "MangaWatch", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
