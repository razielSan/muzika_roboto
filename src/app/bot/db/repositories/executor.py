from typing import List

from app.bot.models import Executor, User, Genre

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ExecutorSqlalchemyRepository:
    model = Executor

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_executor(
        self,
        name: str,
        country: str,
        user: User,
        genres: List[Genre],
    ):
        executor = self.model(
            name=name,
            country=country,
            user=user,
        )
        executor.genres.extend(genres)
        self.session.add(executor)
        await self.session.flush()
        return executor

    async def get_executor(self, user_id: int, executor_id: int):
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.id == executor_id, self.model.user_id == user_id)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        return executor

    async def get_executor_by_name_and_country(
        self, user_id: int, name: str, country: str
    ):
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.name == name,
                self.model.country == country,
            )
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )

        return executor

    async def get_executors_by_name(self, user_id: int, name: str):
        stmt = await self.session.scalars(
            select(self.model)
            .where(
                self.model.user_id == user_id,
                self.model.name == name,
            )
            .order_by(self.model.country)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def get_executors_by_country(self, user_id: int, country: str):
        stmt = await self.session.scalars(
            select(self.model)
            .where(self.model.user_id == user_id, self.model.country == country)
            .order_by(self.model.name)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def get_all_executors_is_user(self, user_id: int):
        stmt = await self.session.scalars(
            select(self.model)
            .where(self.model.user_id == user_id)
            .order_by(self.model.name)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def update_genres(
        self, user_id: int, genres: List[Genre], excutor_id: int
    ):
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.user_id == user_id, self.model.id == excutor_id)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )

        executor.genres = genres
        await self.session.flush()
        return executor

    async def delete_executor(self, user_id: int, executor_id: int):
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.user_id == user_id, self.model.id == executor_id)
            .options(selectinload(self.model.genres))
        )
        if not executor:
            return False

        executor.genres = []
        await self.session.delete(executor)
        await self.session.flush()
        return True
