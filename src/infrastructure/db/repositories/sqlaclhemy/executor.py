from typing import List, Optional, Sequence, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from infrastructure.db.models.sqlaclhemy.user_genre_executor import Genre, Executor
from domain.entities.db.repositories.executor import ExecutorRepository


class SQLAlchemyExecutorRepository(ExecutorRepository):
    model = Executor

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user_executor(
        self,
        user_id: Union[int, None],
        name: str,
        country: str,
        genres: List[Genre],
        file_id: str,
        file_unique_id: str,
    ) -> Executor:
        executor = self.model(
            name=name,
            country=country,
            photo_file_id=file_id,
            photo_file_unique_id=file_unique_id,
            user_id=user_id,
        )
        executor.genres.extend(genres)
        self.session.add(executor)
        await self.session.flush()
        return executor

    async def get_all_executors(
        self, user_id: Optional[int] = None
    ) -> Sequence[Executor]:
        """Возвращает всех исполнителей.

        user_id=None - все исполнители глобальной библиотеки
        user_id=<int> - все исполнители конкретного пользователя
        """

        stmt = await self.session.scalars(
            select(self.model)
            .order_by(self.model.name_lower)
            .where(self.model.user_id.is_(user_id))
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        executors = stmt.all()

        return executors

    async def get_executor(
        self,
        user_id: Union[int, None],
        executor_id: int,
    ) -> Optional[Executor]:
        executor = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.id == executor_id
            )
        )
        return executor

    async def get_executor_by_user_library(
        self,
        executor_id: int,
    ) -> Optional[Executor]:
        executor = await self.session.scalar(
            select(self.model).where(self.model.id == executor_id)
        )
        return executor
