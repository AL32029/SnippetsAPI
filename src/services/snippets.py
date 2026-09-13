import uuid
from typing import cast

from sqlalchemy import or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from models.database import SnippetORM, SnippetURLORM


class SnippetsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save(
        self,
        author_id: int,
        title: str,
        language: str,
        code: str,
    ) -> int:
        snippet = SnippetORM(
            user_id=author_id,
            title=title,
            language=language,
            code=code,
        )

        self.db.add(snippet)

        await self.db.flush()

        return snippet.id

    async def get_by_id(
        self,
        snippet_id: int,
    ) -> "SnippetORM | None":
        snippet = await self.db.get(SnippetORM, snippet_id)
        return cast("SnippetORM | None", cast(object, snippet))

    async def get_by_id_for_user(
        self,
        snippet_id: int,
        user_id: int,
        load_public_urls: bool = False,
    ) -> "SnippetORM | None":
        stmt = select(SnippetORM).where(
            SnippetORM.id == snippet_id,
            SnippetORM.user_id == user_id,
        )

        if load_public_urls:
            stmt = stmt.options(selectinload(SnippetORM.public_urls))

        snippet: SnippetORM | None = await self.db.scalar(stmt)

        return snippet

    async def get_all_by_user(
        self,
        user_id: int,
    ) -> list["SnippetORM"]:
        stmt = select(SnippetORM).where(SnippetORM.user_id == user_id)
        snippets = await self.db.scalars(stmt)
        return cast(list["SnippetORM"], snippets.all())

    async def generate_snippet_url(
        self,
        snippet_id: int,
        is_public: bool,
    ) -> SnippetURLORM:
        snippet_url = SnippetURLORM(snippet_id=snippet_id, is_public=is_public)

        self.db.add(snippet_url)

        await self.db.flush()

        return snippet_url

    async def get_by_shared_url(
        self,
        url_uuid: uuid.UUID,
        user_id: int | None = None,
        with_inc_views_count: bool = True,
    ) -> "SnippetORM | None":
        ownership = (
            or_(
                SnippetURLORM.is_public.is_(True),
                SnippetORM.user_id == user_id,
            )
            if user_id is not None
            else SnippetURLORM.is_public.is_(True)
        )

        stmt = (
            select(SnippetURLORM)
            .join(
                SnippetORM,
                SnippetURLORM.snippet_id == SnippetORM.id,
            )
            .where(
                SnippetURLORM.id == url_uuid,
                ownership,
            )
            .options(contains_eager(SnippetURLORM.snippet))
        )

        url_info: SnippetURLORM | None = await self.db.scalar(stmt)

        if url_info is None:
            return None

        if with_inc_views_count:
            await self.db.execute(
                update(SnippetURLORM)
                .where(SnippetURLORM.id == url_uuid)
                .values(views_count=SnippetURLORM.views_count + 1)
            )

        return url_info.snippet
