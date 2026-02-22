from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models.sqlaclhemy.user_genre_executor import Genre, Executor


class SQLAlchemyExecutorRepository:
    model = Executor

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_user_executor(
        self,
        user_id: int,
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
            user_id=user_id,
        )
        executor.genres.extend(genres)
        self.session.add(executor)
        await self.session.flush()
        return executor
