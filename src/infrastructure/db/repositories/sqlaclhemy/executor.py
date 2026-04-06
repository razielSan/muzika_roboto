from typing import List, Optional, Sequence, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from infrastructure.db.models.sqlaclhemy.user_genre_executor import Genre, Executor
from domain.entities.db.repositories.executor import ExecutorRepository


class SQLAlchemyExecutorRepository(ExecutorRepository):
    model = Executor

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_executor(
        self,
        user_id: Union[int, None],
        name: str,
        country: str,
        genres: List[Genre],
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Executor:
        name_lower = name.casefold()

        executor = self.model(
            name=name,
            country=country,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
            user_id=user_id,
            name_lower=name_lower,
        )
        executor.genres.extend(genres)
        self.session.add(executor)
        await self.session.flush()
        return executor

    async def get_executor_by_name_lower(
        self,
        user_id: Union[None, int],
        name_lower: str,
    ) -> Optional[Executor]:

        # для предотвращения ошибки при сравнивании None
        if user_id is None:
            user_id_condition: bool = self.model.user_id.is_(None)
        else:
            user_id_condition: bool = self.model.user_id == user_id
        executor = await self.session.scalar(
            select(self.model).where(
                self.model.name_lower == name_lower,
                user_id_condition,
            )
        )
        return executor

    async def get_executors_by_name_lower_filter_like(
        self,
        user_id: Union[None, int],
        like: str,
    ) -> Optional[Executor]:

        # для предотвращения ошибки при сравнивании None
        if user_id is None:
            user_id_condition: bool = self.model.user_id.is_(None)
        else:
            user_id_condition: bool = self.model.user_id == user_id
        stmt = await self.session.scalars(
            select(self.model).where(
                self.model.name_lower.like(f"%{like}%"),
                user_id_condition,
            )
        )
        executors = stmt.all()
        return executors

    async def get_executor_by_name_lower_and_country(
        self,
        user_id: Union[None, int],
        name_lower: str,
        country: str,
    ) -> Optional[Executor]:

        # для предотвращения ошибки при сравнивании None
        if user_id is None:
            user_id_condition: bool = self.model.user_id.is_(None)
        else:
            user_id_condition: bool = self.model.user_id == user_id
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.name_lower == name_lower,
                self.model.country == country,
                user_id_condition,
            )
            .options(selectinload(self.model.genres))
        )
        return executor

    async def get_executor_by_name_lower_and_country_from_global_and_user(
        self,
        user_id: int,
        name_lower: str,
        country: str,
    ) -> Optional[Executor]:
        executor = await self.session.scalar(
            select(self.model)
            .where(
                self.model.name_lower == name_lower,
                self.model.country == country,
            )
            .where(or_(self.model.user_id.is_(None), self.model.user_id == user_id))
        )
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
            .order_by(self.model.name_lower)
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

    async def get_global_executor_page(self, page: int) -> Optional[Executor]:
        executor = await self.session.scalar(
            select(self.model)
            .where(self.model.user_id.is_(None))
            .order_by(self.model.name_lower)
            .limit(1)
            .offset(page - 1)
            .options(selectinload(self.model.genres), selectinload(self.model.albums))
        )
        return executor

    async def get_total_executors(self, user_id: Union[None, int]) -> Optional[int]:

        # для предотвращения ошибки при сравнивании None
        if user_id is None:
            condition: bool = self.model.user_id.is_(None)
        else:
            condition: bool = self.model.user_id == user_id

        total_executors = await self.session.scalar(
            select(func.count(self.model.id)).where(condition)
        )
        return total_executors

    async def get_executor_by_user_library(
        self,
        executor_id: int,
    ) -> Optional[Executor]:
        executor = await self.session.scalar(
            select(self.model).where(self.model.id == executor_id)
        )
        return executor

    async def update_executor_photo_file_id(
        self,
        executor_id: int,
        user_id: Optional[int],
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[Executor]:
        executor: Optional[Executor] = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.id == executor_id
            )
        )
        if not executor:
            return None

        executor.photo_file_id = photo_file_id
        executor.photo_file_unique_id = photo_file_unique_id
        await self.session.flush()
        return executor

    async def update_executor_country(
        self,
        executor_id: int,
        user_id: Optional[int],
        country: str,
    ) -> Optional[Executor]:
        executor: Optional[Executor] = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.id == executor_id
            )
        )
        if not executor:
            return None

        executor.country = country
        await self.session.flush()
        return executor

    async def update_executor_genres(
        self, executor_id: int, user_id: Optional[int], genres: List[Genre]
    ) -> Optional[Executor]:
        executor: Optional[Executor] = await self.session.scalar(
            select(self.model)
            .where(self.model.user_id == user_id, self.model.id == executor_id)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.albums))
        )
        if not executor:
            return None

        executor.genres = genres
        await self.session.flush()
        return executor

    async def update_executor_name(
        self, executor_id: int, user_id: Optional[int], name: str
    ) -> Optional[Executor]:
        executor: Optional[Executor] = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.id == executor_id
            )
        )
        if not executor:
            return None

        executor.name = name
        executor.name_lower = name.casefold()
        await self.session.flush()
        return executor

    async def delete_executor(self, user_id: Optional[int], executor_id: int) -> bool:
        # для предотвращения ошибки при сравнивании None
        if user_id is None:
            user_id_condition: bool = self.model.user_id.is_(None)
        else:
            user_id_condition: bool = self.model.user_id == user_id

        executor = await self.session.scalar(
            select(self.model)
            .where(user_id_condition, self.model.id == executor_id)
            .options(selectinload(self.model.genres))
            .options(selectinload(self.model.library_users))
        )

        if not executor:
            return None

        executor.genres = []
        executor.library_users = []
        await self.session.delete(executor)
        await self.session.flush()
        return True
