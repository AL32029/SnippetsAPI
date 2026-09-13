from pydantic import BaseModel, Field


class SnippetCreateSchema(BaseModel):
    title: str = Field(min_length=1, max_length=96)
    language: str = Field(min_length=1, max_length=48)
    code: str = Field(min_length=1)


class SnippetUpdateSchema(BaseModel):
    title: str | None = Field(None, min_length=1, max_length=96)
    language: str | None = Field(None, min_length=1, max_length=48)
    code: str | None = Field(None, min_length=1)


class SnippetInfoSchema(BaseModel):
    id: int
    author_id: int
    title: str
    language: str
    code: str


