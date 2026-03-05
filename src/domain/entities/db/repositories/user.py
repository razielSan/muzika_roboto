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

    @abstractmethod
    async def update_collection_songs_photo_file_id(
        self,
        user_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[User]:
        pass
