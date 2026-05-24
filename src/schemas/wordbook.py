from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class WordBookCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str | None = None


class WordBookRead(BaseModel):
    id: int = Field(..., gt=0)
    name: str
    description: str | None = None
    created_at: datetime
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class WordBookUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = None


class WordBookListResponse(BaseModel):
    items: list[WordBookRead]