import uuid
from typing import Any

from pydantic import BaseModel, field_validator

from schemas.snippets import SnippetInfoSchema


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
