from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from src.config.database import get_db
from src.schemas.wordbook import (
    WordBookCreate,
    WordBookListResponse,
    WordBookRead,
    WordBookUpdate,
)
from src.services import wordbook_service


router = APIRouter(prefix="/wordbooks", tags=["wordbooks"])


@router.post("", response_model=WordBookRead, status_code=status.HTTP_201_CREATED)
def create_wordbook(
    payload: WordBookCreate,
    db: Session = Depends(get_db),
):
    return wordbook_service.create_wordbook(db=db, payload=payload)


@router.get("", response_model=WordBookListResponse)
def list_wordbooks(
    db: Session = Depends(get_db),
):
    wordbooks = wordbook_service.list_wordbooks(db=db)
    return WordBookListResponse(items=wordbooks)


@router.get("/{wordbook_id}", response_model=WordBookRead)
def get_wordbook(
    wordbook_id: int,
    db: Session = Depends(get_db),
):
    return wordbook_service.get_wordbook(db=db, wordbook_id=wordbook_id)


@router.patch("/{wordbook_id}", response_model=WordBookRead)
def update_wordbook(
    wordbook_id: int,
    payload: WordBookUpdate,
    db: Session = Depends(get_db),
):
    return wordbook_service.update_wordbook(
        db=db,
        wordbook_id=wordbook_id,
        payload=payload,
    )


@router.delete("/{wordbook_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_wordbook(
    wordbook_id: int,
    db: Session = Depends(get_db),
):
    wordbook_service.delete_wordbook(db=db, wordbook_id=wordbook_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)