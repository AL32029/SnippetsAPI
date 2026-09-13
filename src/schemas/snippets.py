import uuid
from typing import Any

from pydantic import BaseModel, Field, field_validator


class SnippetCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=96)
    language: str = Field(min_length=1, max_length=48)
    code: str = Field(min_length=1)


class SnippetInfoSchema(BaseModel):
    id: int
    author_id: int
    title: str
    language: str
    code: str


class SnippetURLSchema(BaseModel):
    id: uuid.UUID
    snippet: SnippetInfoSchema | dict
    is_public: bool
    views_count: int

    @field_validator("snippet", mode="before")
    @classmethod
    def validate_snippet(cls, v: Any) -> SnippetInfoSchema | dict:
        if not v:
            return {}

        return v
