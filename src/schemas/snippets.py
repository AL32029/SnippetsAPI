import uuid

from pydantic import BaseModel, Field


class SnippetCreateSchema(BaseModel):
    title: str = Field(max_length=96)
    language: str
    text: str = Field(max_length=2048)


class SnippetInfoSchema(BaseModel):
    id: uuid.UUID
    author_id: int
    title: str = Field(max_length=96)
    language: str
    text: str = Field(max_length=2048)
