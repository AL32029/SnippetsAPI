from typing import cast

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from models.database import UserORM
from services.crypto import CryptoService


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
        user = UserORM(
            name=name,
            email=email,
            password_hash=self.crypto.hash_password(password),
        )

        self.db.add(user)
        await self.db.commit()

    async def login(self, email: str, password: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        user: UserORM | None = await self.db.scalar(stmt)

        if user is None:
            return None

        if not self.crypto.verify_password(password, user.password_hash):
            return None

        return cast("UserORM | None", user)

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        user = await self.db.scalar(stmt)

        return user
