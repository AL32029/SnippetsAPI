from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import session_maker


async def get_db() -> AsyncIterable[AsyncSession]:
    async with session_maker() as session, session.begin():
        yield session
