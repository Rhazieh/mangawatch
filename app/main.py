from fastapi import FastAPI

app = FastAPI(title="MangaWatch", version="0.1.0")


@app.get("/")
def root():
    return {"app": "MangaWatch", "version": "0.1.0"}


@app.get("/health")
def health():
    return {"status": "ok"}
