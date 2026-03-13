from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.db.models.sqlaclhemy.user_genre_executor import UserExecutor


class SQLAlchemyUserExecutorRepository:
    model: UserExecutor = UserExecutor

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def add(self, user_id: int, executor_id: int) -> UserExecutor:
        user_executor: UserExecutor = self.model(
            user_id=user_id, executor_id=executor_id
        )
        self.session.add(user_executor)
        await self.session.flush()
        return user_executor

    async def exists(self, user_id: int, executor_id: int) -> bool:
        user_executor = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.executor_id == executor_id
            )
        )
        return user_executor is not None

    async def delete(self, user_id: int, executor_id: int) -> bool:
        user_executor = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.executor_id == executor_id
            )
        )
        if not user_executor:
            return False
        await self.session.delete(user_executor)
        await self.session.flush()
        return True
