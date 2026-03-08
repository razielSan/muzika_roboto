from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.db.models.album import Album as AlbumDomain


class AlbumRepository(ABC):
    @abstractmethod
    async def get_album(
        self,
        executor_id: int,
        album_id: int,
    ) -> Optional[AlbumDomain]:
        pass
