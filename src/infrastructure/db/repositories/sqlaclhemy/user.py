from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload

from infrastructure.db.models.sqlaclhemy import User
from domain.entities.db.repositories.user import UserRepository
from domain.exceptions.db.user import UserAlreadyExists


class SQLAlchemyUserRepository(UserRepository):
    model: User = User

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user(self, name: str, telegram: int) -> User:
        try:
            user: User = self.model(
                name=name,
                telegram=telegram,
            )

            self.session.add(user)
            await self.session.flush()
            return user
        except IntegrityError:
            raise UserAlreadyExists()

    async def get_user_by_telegram(self, telegram: int) -> Optional[User]:

        user: Optional[User] = await self.session.scalar(
            select(self.model)
            .where(self.model.telegram == telegram)
            .options(selectinload(self.model.library_executors))
        )
        return user

    async def update_collection_songs_photo_file_id(
        self,
        user_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[User]:
        user: Optional[User] = await self.session.scalar(
            select(self.model).where(self.model.id == user_id),
        )
        if not user:
            return None
        user.collection_songs_photo_file_id = photo_file_id
        user.collection_songs_photo_file_unique_id = photo_file_unique_id
        await self.session.flush()
        return user
