from typing import Optional
from abc import abstractmethod, ABC
from typing import List

from domain.entities.db.models.executor import Executor


class ExecutorRepository(ABC):
    @abstractmethod
    async def create_user_executor(
        self,
        user_id: int,
        name: str,
        country: str,
        genres: List,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[Executor]:
        pass
