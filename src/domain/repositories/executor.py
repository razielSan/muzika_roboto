from abc import abstractmethod
from typing import Protocol, List


class ExecutorRepository(Protocol):
    @abstractmethod
    async def create_user_executor(
        self,
        user_id: int,
        name: str,
        country: str,
        genres: List,
        photo_file_id: str,
        photo_file_unique_id: str,
    ):
        pass
