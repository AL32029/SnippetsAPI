import logging
from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import UserORM
from services.crypto import CryptoService

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, db: AsyncSession, crypto: CryptoService):
        self.db = db
        self.crypto = crypto

    async def save(
        self,
        name: str,
        email: str,
        password: str,
    ):
        logger.debug("Password hashing")
        hashed_password = await self.crypto.hash_password_async(password)
        logger.debug("The password has been successfully hashed")

        user = UserORM(
            name=name,
            email=email,
            password_hash=hashed_password,
        )

        logger.debug("Saving the user and sending data to the database")
        self.db.add(user)
        await self.db.flush()
        logger.debug("The user data has been sent to the database")

    async def login(self, email: str, password: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        logger.debug("Requesting user data from the database")
        user = await self.db.scalar(stmt)

        if user is None:
            logger.warning("The requested user is not in the database")
            return None

        logger.debug("The requested user has been found in the database")

        if not await self.crypto.verify_password_async(password, user.password_hash):
            logger.warning(
                "The entered password does not match the "
                "password stored in the database"
            )
            return None

        logger.debug(
            "The entered password matches the password stored in the database. "
            "The user has been successfully authorized"
        )

        return user

    async def get_by_id(self, user_id: str) -> UserORM | None:
        if not user_id.isdigit():
            logger.warning("The passed user_id is not a number")
            return None

        logger.debug("Requesting user data from the database")
        user: UserORM | None = cast(
            "UserORM | None", await self.db.get(UserORM, int(user_id))
        )

        if user is None:
            logger.warning("The requested user is not in the database")
            return None

        logger.debug("The requested user has been found in the database")

        return user
