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
        user_id: int,
        title: str,
        language: str,
        code: str,
    ) -> int:
        snippet = SnippetORM(
            user_id=user_id,
            title=title,
            language=language,
            code=code,
        )

        self.db.add(snippet)

        await self.db.flush()

        return snippet.id

    async def update(
        self,
        snippet_id: int,
        user_id: int,
        title: str | None,
        language: str | None,
        code: str | None,
    ) -> SnippetORM | None:
        snippet = await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
        )

        if snippet is None:
            return None

        if title is not None and snippet.title != title:
            snippet.title = title

        if language is not None and snippet.language != language:
            snippet.language = language

        if code is not None and snippet.code != code:
            snippet.code = code

        await self.db.flush()

        return snippet

    async def delete(
        self,
        snippet_id: int,
        user_id: int,
    ) -> None | bool:
        snippet = await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
        )

        if snippet is None:
            return None

        await self.db.delete(snippet)
        await self.db.flush()
        return True

    async def get_by_id_for_user(
        self,
        snippet_id: int,
        user_id: int,
        load_shared_urls: bool = False,
    ) -> SnippetORM | None:
        return await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
            load_shared_urls=load_shared_urls,
        )

    async def get_all_by_user(
        self,
        user_id: int,
    ) -> list[SnippetORM]:
        stmt = select(SnippetORM).where(SnippetORM.user_id == user_id)
        snippets = await self.db.scalars(stmt)
        return cast(list["SnippetORM"], snippets.all())

    async def generate_snippet_url(
        self,
        user_id: int,
        snippet_id: int,
        is_public: bool,
    ) -> SnippetURLORM | None:
        snippet = await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
        )

        if snippet is None:
            return None

        snippet_url = SnippetURLORM(is_public=is_public)

        snippet.shared_urls.append(snippet_url)

        await self.db.flush()

        return snippet_url

    async def update_snippet_url(
        self,
        user_id: int,
        url_uuid: uuid.UUID,
        is_public: bool,
    ) -> SnippetURLORM | None:
        snippet_url: SnippetURLORM | None = cast(
            "SnippetURLORM | None",
            await self._get_snippet_url_by_id(
                url_uuid=url_uuid,
                user_id=user_id,
                return_info=True,
            ),
        )

        if snippet_url is None:
            return None

        if snippet_url.is_public != is_public:
            snippet_url.is_public = is_public

        await self.db.flush()

        return snippet_url

    async def delete_snippet_url(
        self,
        user_id: int,
        url_uuid: uuid.UUID,
    ) -> None | bool:
        snippet_url: SnippetURLORM | None = cast(
            "SnippetURLORM | None",
            await self._get_snippet_url_by_id(
                url_uuid=url_uuid,
                user_id=user_id,
                return_info=True,
            ),
        )

        if snippet_url is None:
            return None

        await self.db.delete(snippet_url)
        await self.db.flush()
        return True

    async def get_shared_url_info(
        self,
        url_uuid: uuid.UUID,
        user_id: int,
    ) -> SnippetURLORM | None:
        return cast(
            "SnippetURLORM | None",
            await self._get_snippet_url_by_id(
                url_uuid=url_uuid,
                user_id=user_id,
                return_info=True,
            ),
        )

    async def get_by_shared_url(
        self,
        url_uuid: uuid.UUID,
        user_id: int | None = None,
        with_inc_views_count: bool = True,
    ) -> SnippetORM | None:
        return cast(
            "SnippetORM | None",
            await self._get_snippet_url_by_id(
                url_uuid=url_uuid,
                user_id=user_id,
                with_inc_views_count=with_inc_views_count,
                return_info=False,
            ),
        )

    async def _get_snippet_by_id(
        self,
        snippet_id: int,
        user_id: int,
        load_shared_urls: bool = False,
    ) -> SnippetORM | None:
        stmt = select(SnippetORM).where(
            SnippetORM.id == snippet_id,
            SnippetORM.user_id == user_id,
        )

        if load_shared_urls:
            stmt = stmt.options(selectinload(SnippetORM.shared_urls))

        snippet: SnippetORM | None = await self.db.scalar(stmt)

        return snippet

    async def _get_snippet_url_by_id(
        self,
        url_uuid: uuid.UUID,
        user_id: int | None = None,
        with_inc_views_count: bool = False,
        return_info: bool = False,
    ) -> SnippetORM | SnippetURLORM | None:
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

            await self.db.flush()

        return url_info.snippet if not return_info else url_info
