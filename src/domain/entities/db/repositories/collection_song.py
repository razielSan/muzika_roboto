from typing import Sequence, Optional, List
from abc import ABC, abstractmethod

from domain.entities.db.models.collection_song import CollectionSong
from domain.entities.response import CollectionSongResponse


class CollectionSongRepository(ABC):
    @abstractmethod
    async def get_all_songs(
        self,
        user_id: int,
    ) -> Sequence[CollectionSong]:
        pass

    @abstractmethod
    async def get_last_poistion_song(self, user_id: int) -> Optional[int]:
        pass

    @abstractmethod
    async def add_songs(
        self,
        collection_songs: List[CollectionSongResponse],
        user_id: int,
        start_position: int = 1,
    ) -> List:
        pass
