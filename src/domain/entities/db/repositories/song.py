from abc import ABC, abstractmethod
from typing import Optional, List

from domain.entities.db.models.song import Song as SongDomain
from domain.entities.response import SongResponse


class SongRepository(ABC):
    @abstractmethod
    async def get_song(self, album_id: int, song_id: int) -> Optional[SongDomain]:
        pass

    @abstractmethod
    async def get_last_postion_song(self, album_id: int) -> Optional[int]:
        pass

    @abstractmethod
    async def add_songs(
        self,
        songs: List[SongResponse],
        album_id: int,
        start_position: int = 1,
    ) -> List[SongDomain]:
        pass
