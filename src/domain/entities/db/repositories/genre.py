from typing import List, Optional
from abc import abstractmethod, ABC

from domain.entities.db.models.genre import Genre as GenreDomain


class GenreRepository(ABC):
    @abstractmethod
    async def get_or_create_genres(self, titles: List[str]) -> List[GenreDomain]:
        pass

    @abstractmethod
    async def get_genre(self, title: str) -> Optional[GenreDomain]:
        pass
