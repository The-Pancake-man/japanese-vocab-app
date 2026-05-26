from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.vocab_word import VocabWordListResponse
from src.services import quiz_service


router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.get("/words", response_model=VocabWordListResponse)
def get_quiz_words(
    levels: list[str] = Query(..., description="JLPT levels, e.g. N5&levels=N4"),
    db: Session = Depends(get_db),
):
    words = quiz_service.get_quiz_words(db=db, levels=levels)
    return VocabWordListResponse(items=words)