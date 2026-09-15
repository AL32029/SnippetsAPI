import logging
import uuid
from collections.abc import Sequence

from sqlalchemy import ScalarResult, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, selectinload

from models.database import SnippetORM, SnippetURLORM

logger = logging.getLogger(__name__)


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

        logger.debug("Saving the snippet to the database")
        self.db.add(snippet)
        await self.db.flush()
        logger.debug("The snippet has been sent to the database")

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

        log_text = "Changing the snippet %s"

        if title is not None and snippet.title != title:
            logger.debug(log_text, "title")
            snippet.title = title

        if language is not None and snippet.language != language:
            logger.debug(log_text, "language")
            snippet.language = language

        if code is not None and snippet.code != code:
            logger.debug(log_text, "code")
            snippet.code = code

        logger.debug("Sending changes to the database")
        await self.db.flush()
        logger.debug("The changes have been sent to the database")

        return snippet

    async def delete(
        self,
        snippet_id: int,
        user_id: int,
    ) -> bool:
        snippet = await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
        )

        if snippet is None:
            return False

        logger.debug(
            "Deleting the snippet with ID %s from the database",
            snippet_id,
        )
        await self.db.delete(snippet)
        await self.db.flush()
        logger.debug(
            "The snippet with ID %s has been deleted, "
            "and the changes have been sent to the database",
            snippet_id,
        )
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
    ) -> Sequence[SnippetORM]:
        stmt = select(SnippetORM).where(SnippetORM.user_id == user_id)
        logger.debug("Retrieving a list of all user snippets from the database")
        snippets: ScalarResult[SnippetORM] = await self.db.scalars(stmt)
        logger.debug("The list of all user snippets is retrieved from the database")
        return snippets.all()

    async def generate_snippet_url(
        self,
        user_id: int,
        snippet_id: int,
        is_public: bool,
    ) -> SnippetURLORM | None:
        snippet = await self._get_snippet_by_id(
            snippet_id=snippet_id,
            user_id=user_id,
            load_shared_urls=True,
        )

        if snippet is None:
            return None

        snippet_url = SnippetURLORM(is_public=is_public)

        logger.debug("Generating a public link for a snippet with ID %s", snippet.id)
        snippet.shared_urls.append(snippet_url)
        await self.db.flush()
        logger.debug(
            "A public link for a snippet with ID %s has been created; the public link "
            "has been assigned a UUID %s (access level: %s). "
            "The changes have been sent to the database",
            snippet.id,
            snippet_url.id,
            "available to everyone" if is_public else "available only to the author",
        )

        return snippet_url

    async def update_snippet_url(
        self,
        user_id: int,
        url_uuid: uuid.UUID,
        is_public: bool,
    ) -> SnippetURLORM | None:
        snippet_url: SnippetURLORM | None = await self._get_snippet_url_info_by_uuid(
            url_uuid=url_uuid,
            user_id=user_id,
        )

        if snippet_url is None:
            return None

        if snippet_url.is_public != is_public:
            logger.debug(
                "Changing the visibility of the snippet for "
                "a public link (was: %s, now: %s)",
                "available to everyone"
                if snippet_url.is_public
                else "available only to the author",
                "available to everyone"
                if is_public
                else "available only to the author",
            )
            snippet_url.is_public = is_public

        logger.debug("Sending changes to the database")
        await self.db.flush()
        logger.debug("The changes have been sent to the database")

        return snippet_url

    async def delete_snippet_url(
        self,
        user_id: int,
        url_uuid: uuid.UUID,
    ) -> bool:
        snippet_url: SnippetURLORM | None = await self._get_snippet_url_info_by_uuid(
            url_uuid=url_uuid,
            user_id=user_id,
        )

        if snippet_url is None:
            return False

        logger.debug(
            "Deleting the public link with UUID %s from the database",
            url_uuid,
        )
        await self.db.delete(snippet_url)
        await self.db.flush()
        logger.debug(
            "The public link with UUID %s has been deleted, "
            "and the changes have been sent to the database",
            url_uuid,
        )
        return True

    async def get_url_info_by_uuid(
        self,
        url_uuid: uuid.UUID,
        user_id: int,
    ) -> SnippetURLORM | None:
        return await self._get_snippet_url_info_by_uuid(
            url_uuid=url_uuid,
            user_id=user_id,
        )

    async def get_snippet_by_url_uuid(
        self,
        url_uuid: uuid.UUID,
        user_id: int | None = None,
    ) -> SnippetORM | None:
        return await self._get_snippet_by_url_uuid(
            url_uuid=url_uuid,
            user_id=user_id,
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

        logger.debug(
            "Retrieving a snippet from the database %s",
            "with the loading of public links"
            if load_shared_urls
            else "without loading public links",
        )
        snippet: SnippetORM | None = await self.db.scalar(stmt)

        if snippet is None:
            logger.warning("The requested snippet is not in the database")
        else:
            logger.debug("The requested snippet was obtained from the database")

        return snippet

    async def _get_snippet_url_info_by_uuid(
        self,
        url_uuid: uuid.UUID,
        user_id: int,
    ) -> SnippetURLORM | None:
        stmt = (
            select(SnippetURLORM)
            .join(
                SnippetORM,
                SnippetURLORM.snippet_id == SnippetORM.id,
            )
            .where(
                SnippetURLORM.id == url_uuid,
                SnippetORM.user_id == user_id,
            )
            .options(contains_eager(SnippetURLORM.snippet))
        )

        logger.debug(
            "Obtaining information about a public link "
            "with a UUID %s from the database",
            url_uuid,
        )
        url_info: SnippetURLORM | None = await self.db.scalar(stmt)

        if url_info is None:
            logger.warning(
                "The public link with UUID %s was not found in the database",
                url_uuid,
            )
            return None

        logger.debug(
            "The public link with UUID %s was found in the database",
            url_uuid,
        )

        return url_info

    async def _get_snippet_by_url_uuid(
        self,
        url_uuid: uuid.UUID,
        user_id: int | None = None,
    ) -> SnippetORM | None:
        ownership = (
            or_(
                SnippetURLORM.is_public.is_(True),
                SnippetORM.user_id == user_id,
            )
            if user_id is not None
            else SnippetURLORM.is_public.is_(True)
        )

        stmt = (
            select(SnippetORM)
            .join(SnippetURLORM, SnippetURLORM.snippet_id == SnippetORM.id)
            .where(SnippetURLORM.id == url_uuid, ownership)
        )

        logger.debug("Retrieving a snippet via a public link with a UUID %s", url_uuid)
        url_info: SnippetORM | None = await self.db.scalar(stmt)

        if url_info is None:
            logger.warning(
                "A snippet based on a public link with UUID %s, "
                "matching the user’s access level, was not found in the database",
                url_uuid,
            )
            return None

        logger.debug(
            "A snippet based on the public link with UUID %s, "
            "matching the user’s access level, has been found in the database",
            url_uuid,
        )

        logger.debug("Increasing the snippet view counter via a public link")
        await self.db.execute(
            update(SnippetURLORM)
            .where(SnippetURLORM.id == url_uuid)
            .values(views_count=SnippetURLORM.views_count + 1)
        )

        await self.db.flush()
        logger.debug(
            "The snippet view counter for the public link has been increased, "
            "and the changes have been sent to the database"
        )

        return url_info
