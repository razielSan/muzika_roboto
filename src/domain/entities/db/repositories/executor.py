from typing import Optional, Sequence, Union
from abc import abstractmethod, ABC
from typing import List

from domain.entities.db.models.executor import Executor as DomainExecutor


class ExecutorRepository(ABC):
    @abstractmethod
    async def create_user_executor(
        self,
        user_id: Union[int, None],
        name: str,
        country: str,
        genres: List,
        photo_file_id: str,
        photo_file_unique_id: str,
        name_lower: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_all_executors(
        self, user_id: Optional[int] = None
    ) -> Sequence[DomainExecutor]:
        pass

    @abstractmethod
    async def get_executor(
        self,
        user_id: Union[int, None],
        executor_id: int,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_executor_by_user_library(
        self,
        executor_id: int,
    ) -> Optional[DomainExecutor]:
        pass
