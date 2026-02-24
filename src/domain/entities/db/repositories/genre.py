from typing import List
from abc import abstractmethod, ABC

from domain.entities.db.models.genre import Genre


class GenreRepository(ABC):
    @abstractmethod
    async def get_or_create_genres(self, titles: List[str]) -> List[Genre]:
        pass
