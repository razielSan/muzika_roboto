from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from sqlalchemy.exc import IntegrityError

from infrastructure.db.models.sqlaclhemy import User
from domain.entities.db.repositories.user import UserRepository
from domain.exceptions.db.user import UserAlreadyExists


class SQLAlchemyUserRepository(UserRepository):
    model = User

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_user(self, name: str, telegram: int) -> User:
        try:
            user = self.model(
                name=name,
                telegram=telegram,
            )

            self.session.add(user)
            await self.session.flush()
            return user
        except IntegrityError:
            raise UserAlreadyExists()

    async def get_user_by_telegram(self, telegram: int) -> Optional[User]:

        user = await self.session.scalar(
            select(self.model).where(self.model.telegram == telegram)
        )
        return user
