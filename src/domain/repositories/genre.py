from typing import List

from abc import abstractmethod
from typing import Protocol


class GenreRepository(Protocol):
    @abstractmethod
    async def get_or_create_genres(self, titles: List[str]) -> List:
        pass
