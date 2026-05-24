from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.wordbook import WordBook
from src.schemas.wordbook import WordBookCreate, WordBookUpdate

# Handles CRUD operations for wordbooks

def get_wordbook_or_404(db: Session, wordbook_id: int) -> WordBook:
    wordbook = db.query(WordBook).filter(WordBook.id == wordbook_id).first()

    if wordbook is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="WordBook not found",
        )

    return wordbook


def create_wordbook(db: Session, payload: WordBookCreate) -> WordBook:
    existing_wordbook = (
        db.query(WordBook)
        .filter(WordBook.name == payload.name)
        .first()
    )

    if existing_wordbook is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="WordBook name already exists",
        )

    wordbook = WordBook(
        name=payload.name,
        description=payload.description,
    )

    db.add(wordbook)
    db.commit()
    db.refresh(wordbook)

    return wordbook


def list_wordbooks(db: Session) -> list[WordBook]:
    return (
        db.query(WordBook)
        .order_by(WordBook.id.desc())
        .all()
    )


def get_wordbook(db: Session, wordbook_id: int) -> WordBook:
    return get_wordbook_or_404(db, wordbook_id)


def update_wordbook(
    db: Session,
    wordbook_id: int,
    payload: WordBookUpdate,
) -> WordBook:
    wordbook = get_wordbook_or_404(db, wordbook_id)

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if "name" in update_data:
        existing_wordbook = (
            db.query(WordBook)
            .filter(
                WordBook.name == update_data["name"],
                WordBook.id != wordbook_id,
            )
            .first()
        )

        if existing_wordbook is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="WordBook name already exists",
            )

    for field, value in update_data.items():
        setattr(wordbook, field, value)

    db.commit()
    db.refresh(wordbook)

    return wordbook


def delete_wordbook(db: Session, wordbook_id: int) -> None:
    wordbook = get_wordbook_or_404(db, wordbook_id)

    db.delete(wordbook)
    db.commit()