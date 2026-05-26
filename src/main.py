from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.config.database import Base, engine
from src.models import WordBook, VocabWord
from src.routes import quiz, wordbooks, words


STATIC_DIR = Path(__file__).resolve().parent / "static"

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Japanese Vocabulary API",
    description="JLPT Vocabulary Learning System",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def read_root():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return FileResponse(index_path)
    return {"message": "Japanese Vocabulary API is running"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "message": "Japanese Vocabulary API is running",
    }


app.include_router(wordbooks.router)
app.include_router(words.router)
app.include_router(quiz.router)