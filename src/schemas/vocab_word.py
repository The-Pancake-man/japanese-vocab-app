from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

# schsma help us filters out invalid data.

JLPTLevel = Literal["N1", "N2", "N3", "N4", "N5"]
PartOfSpeech = Literal[
    "noun",
    "verb",
    "i_adjective",
    "na_adjective",
    "adverb",
    "expression",
    "other",
]


class VocabWordCreate(BaseModel):
    wordbook_id: int = Field(..., gt=0)
    word: str = Field(..., min_length=1, max_length=100)
    hiragana: str | None = Field(default=None, max_length=100)
    jlpt_level: JLPTLevel
    part_of_speech: PartOfSpeech
    meaning_zh: str = Field(..., min_length=1)


class VocabWordRead(BaseModel):
    id: int = Field(..., gt=0)
    wordbook_id: int
    word: str
    hiragana: str | None = None
    jlpt_level: str
    part_of_speech: str
    meaning_zh: str
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


# wordbook_id: Must be greater than 0.
# word: Cannot be empty.
# hiragana: Can be empty.(Optional)
# jlpt_level: Must be one of the following: N1, N2, N3, N4, N5.
# part_of_speech: Must be a valid/specified part of speech.
# meaning_zh: Cannot be empty. (Required)
class VocabWordUpdate(BaseModel):
    wordbook_id: int | None = Field(default=None, gt=0)
    word: str | None = Field(default=None, min_length=1, max_length=100)
    hiragana: str | None = Field(default=None, max_length=100)
    jlpt_level: JLPTLevel | None = None
    part_of_speech: PartOfSpeech | None = None
    meaning_zh: str | None = Field(default=None, min_length=1)


class VocabWordListResponse(BaseModel):
    items: list[VocabWordRead]