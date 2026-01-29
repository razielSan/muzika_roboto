from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.bot.models import User


class UserSqlalchemyRepository:

    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, name: str, telegram: int) -> User:

        user = User(
            name=name,
            telegram=telegram,
        )

        self.session.add(user)
        await self.session.flush()
        return user

    async def get_user_by_telegram(self, telegram: int) -> Optional[User]:

        user = await self.session.scalar(
            select(self.model).where(self.model.telegram == telegram)
        )
        return user
