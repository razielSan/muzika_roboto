from abc import abstractmethod
from typing import Protocol


class UserRepository(Protocol):
    @abstractmethod
    async def create_user(self, name: str, telegram: int):
        pass

    @abstractmethod
    async def get_user_by_telegram(self, telegram: int):
        pass
