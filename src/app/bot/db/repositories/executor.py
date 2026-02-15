from typing import List

from app.bot.models import Executor, Genre

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class ExecutorSqlalchemyRepository:
    model = Executor

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_base_executor(
        self,
        name: str,
        country: str,
        genres: List[Genre],
        file_id: str,
        file_unique_id: str,
    ):
        executor = self.model(
            name=name,
            country=country,
            photo_file_id=file_id,
            photo_file_unique_id=file_unique_id,
        )
        executor.genres.extend(genres)
        self.session.add(executor)
        await self.session.flush()
        return executor

    async def get_base_executor(self, executor_id: int):
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.id == executor_id,
            )
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        return executor

    async def get_all_executors(self):
        stmt = await self.session.scalars(
            select(self.model)
            .order_by(self.model.name)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def get_base_executor_by_name_and_country(self, name: str, country: str):
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.name == name,
                self.model.country == country,
            )
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )

        return executor

    async def get_base_executors_by_name(self, name: str):
        stmt = await self.session.scalars(
            select(self.model)
            .where(
                self.model.name == name,
            )
            .order_by(self.model.country)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def get_base_executors_by_country(self, country: str):
        stmt = await self.session.scalars(
            select(self.model)
            .where(self.model.country == country)
            .order_by(self.model.name)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()
        return executors

    async def get_all_albums_is_base_executor(
        self,
        executor_id: int,
    ):
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.id == executor_id,
            )
            .order_by(self.model.name)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        return executor.albums

    async def update_genres_base_executor(
        self,
        genres: List[Genre],
        excutor_id: int,
    ):
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.id == excutor_id)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )

        executor.genres = genres
        await self.session.flush()
        return executor

    async def update_photo_file_id_and_photo_file_unique_id(
        self,
        executor_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ):
        executor = await self.session.scalar(
            select(self.model).where(self.model.id == executor_id)
        )
        executor.photo_file_id = photo_file_id
        executor.photo_file_unique_id = photo_file_unique_id
        await self.session.flush()
        return executor

    async def update_name(
        self,
        executor_id: int,
        name: str,
    ):
        executor = await self.session.scalar(
            select(self.model).where(self.model.id == executor_id)
        )
        executor.name = name
        await self.session.flush()
        return executor

    async def update_country(
        self,
        executor_id: int,
        country: str,
    ):
        executor = await self.session.scalar(
            select(self.model).where(self.model.id == executor_id)
        )
        executor.country = country
        await self.session.flush()
        return executor

    async def delete_base_executor(self, executor_id: int):
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.id == executor_id)
            .options(selectinload(self.model.genres))
        )

        if not executor:
            return False

        executor.genres = []
        await self.session.delete(executor)
        await self.session.flush()
        return True
