from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.db.models.album import Album as AlbumDomain


class AlbumRepository(ABC):
    @abstractmethod
    async def create_album(
        self,
        executor_id: int,
        title: str,
        year: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> AlbumDomain:
        pass

    @abstractmethod
    async def get_album(
        self,
        executor_id: int,
        album_id: int,
    ) -> Optional[AlbumDomain]:
        pass

    @abstractmethod
    async def get_album_by_title(
        self,
        executor_id: int,
        title: str,
    ) -> Optional[AlbumDomain]:
        pass

    @abstractmethod
    async def update_photo_file_id(
        self,
        executor_id: int,
        album_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Optional[AlbumDomain]:
        pass

    @abstractmethod
    async def update_year(
        self, executor_id: int, album_id: int, year: int
    ) -> Optional[AlbumDomain]:
        pass

    @abstractmethod
    async def update_title(
        self, executor_id: int, album_id: int, title: str
    ) -> Optional[AlbumDomain]:
        pass

    @abstractmethod
    async def delete_album(
        self,
        executor_id: int,
        album_id: int,
    ) -> bool:
        pass
