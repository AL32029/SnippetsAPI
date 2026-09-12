from typing import Annotated

from fastapi import APIRouter
from fastapi.params import Depends

from models.database import UserORM
from schemas.snippets import SnippetCreateSchema, SnippetInfoSchema
from services.dependencies import get_current_user

snippets_router = APIRouter(prefix="/snippets", tags=["Snippets"])


@snippets_router.post("/create", response_model=SnippetInfoSchema)
async def create_snippet_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippet_data: SnippetCreateSchema,
) -> SnippetInfoSchema:
    # TODO: Реализовать создание сниппетов
    pass


# TODO: Добавить эндпоинт генерации ссылки для доступа к сниппету
# TODO: Добавить эндпоинт для получения списка сниппетов
# TODO: Добавить эндпоинт для удаления сниппетов
# TODO: Добавить эндпоинт для просмотра сниппетов по UUID
