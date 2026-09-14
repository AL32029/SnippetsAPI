import logging
from collections.abc import AsyncIterable

from sqlalchemy.ext.asyncio import AsyncSession

from db.engine import session_maker

logger = logging.getLogger(__name__)


async def get_db() -> AsyncIterable[AsyncSession]:
    logger.debug("Creating a database session")
    async with session_maker() as session, session.begin():
        logger.debug("The database session has been created")
        yield session
        logger.debug("Closing the database session")
    logger.debug("The database session is closed")
