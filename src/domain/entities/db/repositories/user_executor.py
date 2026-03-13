from abc import ABC, abstractmethod

from domain.entities.db.models.user_executor import UserExecutor as UserExecutorDomain


class UserExecutorRepository(ABC):
    @abstractmethod
    async def add(self, user_id: int, executor_id: int) -> UserExecutorDomain:
        pass

    @abstractmethod
    async def exists(self, user_id: int, executor_id: int) -> bool:
        pass

    @abstractmethod
    async def delete(self, user_id: int, executor_id: int) -> bool:
        pass
