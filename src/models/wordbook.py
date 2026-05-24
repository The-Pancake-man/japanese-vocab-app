from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.config.database import Base


class WordBook(Base):
    __tablename__ = "wordbooks"

    id = Column(Integer, primary_key=True, index=True)

    name = Column(String(100), nullable=False, unique=True, index=True)
    description = Column(Text, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now()
    )

    # One WordBook has many VocabWords
    vocab_words = relationship(
        "VocabWord",
        back_populates="wordbook",
        cascade="all, delete-orphan"
    )