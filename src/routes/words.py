from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.vocab_word import (
    VocabWordCreate,
    VocabWordListResponse,
    VocabWordRead,
    VocabWordUpdate,
)
from src.services import vocab_service


router = APIRouter(prefix="/words", tags=["words"])


@router.post("", response_model=VocabWordRead, status_code=status.HTTP_201_CREATED)
def create_vocab_word(
    payload: VocabWordCreate,
    db: Session = Depends(get_db),
):
    return vocab_service.create_vocab_word(db=db, payload=payload)


@router.get("", response_model=VocabWordListResponse)
def list_vocab_words(
    wordbook_id: int | None = Query(default=None),
    jlpt_level: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    words = vocab_service.list_vocab_words(
        db=db,
        wordbook_id=wordbook_id,
        jlpt_level=jlpt_level,
    )
    return VocabWordListResponse(items=words)


@router.get("/{word_id}", response_model=VocabWordRead)
def get_vocab_word(
    word_id: int,
    db: Session = Depends(get_db),
):
    return vocab_service.get_vocab_word(db=db, word_id=word_id)


@router.patch("/{word_id}", response_model=VocabWordRead)
def update_vocab_word(
    word_id: int,
    payload: VocabWordUpdate,
    db: Session = Depends(get_db),
):
    return vocab_service.update_vocab_word(
        db=db,
        word_id=word_id,
        payload=payload,
    )


@router.delete("/{word_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vocab_word(
    word_id: int,
    db: Session = Depends(get_db),
):
    vocab_service.delete_vocab_word(db=db, word_id=word_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)