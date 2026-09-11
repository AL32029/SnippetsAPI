from typing import Annotated, cast

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from db.dependencies import get_db
from models.database_models import UserORM


class UserService:
    def __init__(self, db: Annotated[AsyncSession, Depends(get_db)]):
        self.db = db

    async def get_by_id(self, user_id: int) -> UserORM | None:
        user = await self.db.get(UserORM, user_id)

        return cast("UserORM | None", user)

    async def get_by_email(self, email: str) -> UserORM | None:
        stmt = select(UserORM).where(UserORM.email == email)
        user = await self.db.scalar(stmt)

        return user
