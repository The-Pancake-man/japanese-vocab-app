from fastapi import FastAPI

app = FastAPI(
    title="Japanese Vocabulary API",
    description="JLPT Vocabulary Learning System",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "Japanese Vocabulary API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}