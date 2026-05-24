from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.vocab_word import VocabWord
from src.schemas.vocab_word import VocabWordCreate, VocabWordUpdate
from src.services.wordbook_service import get_wordbook_or_404

# Handles CRUD operations for vocabulary words (VocabWord).
# It depends on wordbook_service to verify that the wordbook_id exists before adding a new word.

def get_vocab_word_or_404(db: Session, word_id: int) -> VocabWord:
    vocab_word = db.query(VocabWord).filter(VocabWord.id == word_id).first()

    if vocab_word is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vocab word not found",
        )

    return vocab_word


def create_vocab_word(db: Session, payload: VocabWordCreate) -> VocabWord:
    get_wordbook_or_404(db, payload.wordbook_id)

    vocab_word = VocabWord(
        wordbook_id=payload.wordbook_id,
        word=payload.word,
        hiragana=payload.hiragana,
        jlpt_level=payload.jlpt_level,
        part_of_speech=payload.part_of_speech,
        meaning_zh=payload.meaning_zh,
    )

    db.add(vocab_word)
    db.commit()
    db.refresh(vocab_word)

    return vocab_word


def list_vocab_words(
    db: Session,
    wordbook_id: int | None = None,
    jlpt_level: str | None = None,
) -> list[VocabWord]:
    query = db.query(VocabWord)

    if wordbook_id is not None:
        get_wordbook_or_404(db, wordbook_id)
        query = query.filter(VocabWord.wordbook_id == wordbook_id)

    if jlpt_level is not None:
        query = query.filter(VocabWord.jlpt_level == jlpt_level)

    return (
        query
        .order_by(VocabWord.id.desc())
        .all()
    )


def get_vocab_word(db: Session, word_id: int) -> VocabWord:
    return get_vocab_word_or_404(db, word_id)


def update_vocab_word(
    db: Session,
    word_id: int,
    payload: VocabWordUpdate,
) -> VocabWord:
    vocab_word = get_vocab_word_or_404(db, word_id)

    update_data = payload.model_dump(exclude_unset=True)

    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields to update",
        )

    if "wordbook_id" in update_data:
        get_wordbook_or_404(db, update_data["wordbook_id"])

    for field, value in update_data.items():
        setattr(vocab_word, field, value)

    db.commit()
    db.refresh(vocab_word)

    return vocab_word


def delete_vocab_word(db: Session, word_id: int) -> None:
    vocab_word = get_vocab_word_or_404(db, word_id)

    db.delete(vocab_word)
    db.commit()