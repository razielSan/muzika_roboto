from abc import ABC, abstractmethod
from typing import Optional

from domain.entities.db.models.song import Song as SongDomain


class SongRepository(ABC):
    @abstractmethod
    async def get_song(self, album_id: int, song_id: int) -> Optional[SongDomain]:
        pass
