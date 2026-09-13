import uuid
from typing import Annotated

from fastapi import APIRouter, HTTPException, Response
from fastapi.params import Depends
from starlette.status import HTTP_204_NO_CONTENT, HTTP_404_NOT_FOUND

from models.database import UserORM
from schemas.snippets import (
    SnippetCreateSchema,
    SnippetInfoSchema,
    SnippetUpdateSchema,
)
from schemas.snippets_url import SnippetURLSchema, SnippetURLSharingSchema
from services.dependencies import (
    get_current_user,
    get_current_user_optional,
    get_snippets_service,
)
from services.snippets import SnippetsService

snippets_router = APIRouter(prefix="/snippets")


@snippets_router.post(
    "/create",
    response_model=SnippetInfoSchema,
    tags=["Snippets Actions"],
)
async def create_snippet_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_data: SnippetCreateSchema,
) -> SnippetInfoSchema:
    snippet_uuid = await snippets_service.save(
        user_id=user.id,
        title=snippet_data.title,
        language=snippet_data.language,
        code=snippet_data.code,
    )

    return SnippetInfoSchema(
        id=snippet_uuid,
        author_id=user.id,
        title=snippet_data.title,
        language=snippet_data.language,
        code=snippet_data.code,
    )


@snippets_router.get(
    "/list",
    response_model=list[SnippetInfoSchema],
    tags=["Snippets Actions"],
)
async def all_user_snippets_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
) -> list[SnippetInfoSchema]:
    snippets = await snippets_service.get_all_by_user(user_id=user.id)

    return [
        SnippetInfoSchema(
            id=snippet.id,
            author_id=snippet.user_id,
            title=snippet.title,
            language=snippet.language,
            code=snippet.code,
        )
        for snippet in snippets
    ]


@snippets_router.get(
    "/{snippet_id}",
    response_model=SnippetInfoSchema,
    tags=["Snippets Actions"],
)
async def snippet_info_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_id: int,
) -> SnippetInfoSchema:
    snippet = await snippets_service.get_by_id_for_user(
        snippet_id=snippet_id,
        user_id=user.id,
    )

    if snippet is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet with ID {snippet_id} was not found",
        )

    return SnippetInfoSchema(
        id=snippet.id,
        author_id=snippet.user_id,
        title=snippet.title,
        language=snippet.language,
        code=snippet.code,
    )


@snippets_router.put(
    "/{snippet_id}",
    response_model=SnippetInfoSchema,
    tags=["Snippets Actions"],
)
async def update_snippet_data_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_id: int,
    snippet_data: SnippetUpdateSchema,
) -> SnippetInfoSchema:
    snippet = await snippets_service.update(
        snippet_id=snippet_id,
        user_id=user.id,
        title=snippet_data.title,
        language=snippet_data.language,
        code=snippet_data.code,
    )

    if snippet is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet with ID {snippet_id} was not found",
        )

    return SnippetInfoSchema(
        id=snippet.id,
        author_id=snippet.user_id,
        title=snippet.title,
        language=snippet.language,
        code=snippet.code,
    )


@snippets_router.delete(
    "/{snippet_id}",
    tags=["Snippets Actions"],
)
async def delete_snippet_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_id: int,
) -> Response:
    deleted = await snippets_service.delete(
        snippet_id=snippet_id,
        user_id=user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet with ID {snippet_id} was not found",
        )

    return Response(status_code=HTTP_204_NO_CONTENT)


@snippets_router.post(
    "/{snippet_id}/share",
    response_model=SnippetURLSchema,
    tags=["Snippets Actions"],
)
async def share_snippet_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_id: int,
    url_info: SnippetURLSharingSchema,
) -> SnippetURLSchema:
    snippet = await snippets_service.get_by_id_for_user(
        snippet_id=snippet_id,
        user_id=user.id,
    )

    if snippet is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet with ID {snippet_id} was not found",
        )

    snippet_url = await snippets_service.generate_snippet_url(
        user_id=user.id,
        snippet_id=snippet.id,
        is_public=url_info.is_public,
    )

    return SnippetURLSchema(
        id=snippet_url.id,
        snippet=SnippetInfoSchema(
            id=snippet.id,
            author_id=snippet.user_id,
            title=snippet.title,
            language=snippet.language,
            code=snippet.code,
        )
        if url_info.return_snippet_info
        else None,
        is_public=snippet_url.is_public,
        views_count=snippet_url.views_count,
    )


@snippets_router.get(
    "/{snippet_id}/shared_urls",
    response_model=list[SnippetURLSchema],
    tags=["Snippets Shared URLs Actions"],
)
async def all_shared_urls_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    snippet_id: int,
) -> list[SnippetURLSchema]:
    snippet = await snippets_service.get_by_id_for_user(
        snippet_id=snippet_id,
        user_id=user.id,
        load_shared_urls=True,
    )

    if snippet is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet with ID {snippet_id} was not found",
        )

    return [
        SnippetURLSchema(
            id=url.id,
            snippet=None,
            is_public=url.is_public,
            views_count=url.views_count,
        )
        for url in snippet.shared_urls
    ]


@snippets_router.get(
    "/shared/{url_uuid}/info",
    response_model=SnippetURLSchema,
    tags=["Snippets Shared URLs Actions"],
)
async def get_shared_url_info_endpoint(
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    url_uuid: uuid.UUID,
    user: Annotated[UserORM, Depends(get_current_user)],
    return_snippet_info: bool = True,
) -> SnippetURLSchema:
    snippet_url = await snippets_service.get_shared_url_info(
        url_uuid=url_uuid,
        user_id=user.id,
    )

    if snippet_url is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The public link {url_uuid} was not found",
        )

    return SnippetURLSchema(
        id=snippet_url.id,
        snippet=SnippetInfoSchema(
            id=snippet_url.snippet.id,
            author_id=snippet_url.snippet.user_id,
            title=snippet_url.snippet.title,
            language=snippet_url.snippet.language,
            code=snippet_url.snippet.code,
        )
        if return_snippet_info
        else None,
        is_public=snippet_url.is_public,
        views_count=snippet_url.views_count,
    )


@snippets_router.get(
    "/shared/{url_uuid}",
    response_model=SnippetInfoSchema,
    tags=["Snippets Shared URLs Actions"],
)
async def get_snippet_by_uuid_endpoint(
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    url_uuid: uuid.UUID,
    user: Annotated[UserORM | None, Depends(get_current_user_optional)] = None,
) -> SnippetInfoSchema:
    snippet = await snippets_service.get_by_shared_url(
        url_uuid=url_uuid,
        user_id=user.id if user is not None else None,
    )

    if snippet is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The snippet for the public link {url_uuid} was not found",
        )

    return SnippetInfoSchema(
        id=snippet.id,
        author_id=snippet.user_id,
        title=snippet.title,
        language=snippet.language,
        code=snippet.code,
    )


@snippets_router.put(
    "/shared/{url_uuid}",
    response_model=SnippetURLSchema,
    tags=["Snippets Shared URLs Actions"],
)
async def update_snippet_url_endpoint(
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    url_uuid: uuid.UUID,
    user: Annotated[UserORM, Depends(get_current_user_optional)],
    url_info: SnippetURLSharingSchema,
) -> SnippetURLSchema:
    snippet_url = await snippets_service.update_snippet_url(
        url_uuid=url_uuid,
        user_id=user.id,
        is_public=url_info.is_public,
    )

    if snippet_url is None:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The public link {url_uuid} was not found",
        )

    return SnippetURLSchema(
        id=snippet_url.id,
        snippet=SnippetInfoSchema(
            id=snippet_url.snippet.id,
            author_id=snippet_url.snippet.user_id,
            title=snippet_url.snippet.title,
            language=snippet_url.snippet.language,
            code=snippet_url.snippet.code,
        )
        if url_info.return_snippet_info
        else None,
        is_public=snippet_url.is_public,
        views_count=snippet_url.views_count,
    )


@snippets_router.delete(
    "/shared/{url_uuid}",
    tags=["Snippets Shared URLs Actions"],
)
async def delete_snippet_url_endpoint(
    user: Annotated[UserORM, Depends(get_current_user)],
    snippets_service: Annotated[SnippetsService, Depends(get_snippets_service)],
    url_uuid: uuid.UUID,
) -> Response:
    deleted = await snippets_service.delete_snippet_url(
        url_uuid=url_uuid,
        user_id=user.id,
    )

    if not deleted:
        raise HTTPException(
            status_code=HTTP_404_NOT_FOUND,
            detail=f"The public link {url_uuid} was not found",
        )

    return Response(status_code=HTTP_204_NO_CONTENT)
