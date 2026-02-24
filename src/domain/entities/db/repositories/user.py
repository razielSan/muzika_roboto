from typing import Optional
from abc import abstractmethod, ABC

from domain.entities.db.models.user import User


class UserRepository(ABC):
    @abstractmethod
    async def create_user(self, name: str, telegram: int) -> Optional[User]:
        pass

    @abstractmethod
    async def get_user_by_telegram(self, telegram: int) -> Optional[User]:
        pass
