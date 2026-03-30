from typing import Optional, Sequence, Union
from abc import abstractmethod, ABC
from typing import List

from domain.entities.db.models.executor import Executor as DomainExecutor
from domain.entities.db.models.genre import Genre as DomainGenre


class ExecutorRepository(ABC):
    @abstractmethod
    async def create_executor(
        self,
        user_id: Union[int, None],
        name: str,
        country: str,
        genres: List,
        photo_file_id: str,
        photo_file_unique_id: str,
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

    @abstractmethod
    async def get_global_executor_page(self, page: int) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_total_executors(self, user_id: Optional[int]) -> Optional[int]:
        pass

    @abstractmethod
    async def get_executor_by_name_lower(
        self,
        user_id: Union[None, int],
        name_lower: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_executors_by_name_lower_filter_like(
        self,
        user_id: Union[None, int],
        name_lower: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_executor_by_name_lower_and_country(
        self,
        user_id: Union[None, int],
        name_lower: str,
        country: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def get_executor_by_name_lower_and_country_from_global_and_user(
        self,
        user_id: int,
        name_lower: str,
        country: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def delete_executor(
        self,
        user_id: Optional[int],
        executor_id: int,
    ) -> bool:
        pass

    @abstractmethod
    async def update_executor_photo_file_id(
        self,
        executor_id: int,
        user_id: Optional[int],
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def update_executor_country(
        self,
        executor_id: int,
        user_id: Optional[int],
        country: str,
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def update_executor_genres(
        self, executor_id: int, user_id: Optional[int], genres: List[DomainGenre]
    ) -> Optional[DomainExecutor]:
        pass

    @abstractmethod
    async def update_executor_name(
        self, executor_id: int, user_id: Optional[int], name: str
    ) -> Optional[DomainExecutor]:
        pass
