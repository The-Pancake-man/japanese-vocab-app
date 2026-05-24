from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from src.models.vocab_word import VocabWord

# Handles future quiz logic, such as filtering words by JLPT levels.

VALID_JLPT_LEVELS = {"N1", "N2", "N3", "N4", "N5"}


def get_quiz_words(
    db: Session,
    levels: list[str],
) -> list[VocabWord]:
    if not levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="At least one JLPT level must be selected",
        )

    invalid_levels = [level for level in levels if level not in VALID_JLPT_LEVELS]

    if invalid_levels:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid JLPT level: {invalid_levels}",
        )

    words = (
        db.query(VocabWord)
        .filter(VocabWord.jlpt_level.in_(levels))
        .order_by(VocabWord.id.desc())
        .all()
    )

    if not words:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No vocabulary words found for selected levels",
        )

    return words