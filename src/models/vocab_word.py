from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, UniqueConstraint

from src.config.database import Base


class VocabWord(Base):
    __tablename__ = "vocab_words"

    __table_args__ = (
        UniqueConstraint("wordbook_id", "word", name="uq_wordbook_word"),
    )

    id = Column(Integer, primary_key=True, index=True)

    wordbook_id = Column(
        Integer,
        ForeignKey("wordbooks.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    word = Column(String(100), nullable=False, index=True)
    hiragana = Column(String(100), nullable=True)

    jlpt_level = Column(String(10), nullable=False, index=True)
    part_of_speech = Column(String(50), nullable=False)

    meaning_zh = Column(Text, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # Each VocabWord belongs to one WordBook
    wordbook = relationship(
        "WordBook",
        back_populates="vocab_words"
    )