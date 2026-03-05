from typing import Sequence, Optional, List
from abc import ABC, abstractmethod

from domain.entities.db.models.collection_songs import CollectionSongs


class CollectionSongsRepository(ABC):
    @abstractmethod
    async def get_all_songs(
        self,
        user_id: int,
    ) -> Sequence[CollectionSongs]:
        pass

    @abstractmethod
    async def get_song(self, user_id: int, song_id: int) -> Optional[CollectionSongs]:
        pass

    @abstractmethod
    async def get_last_poistion_song(self, user_id: int) -> Optional[int]:
        pass

    @abstractmethod
    async def add_songs(
        self,
        collection_songs: List[CollectionSongs],
        user_id: int,
        start_position: int = 1,
    ) -> List:
        pass

    @abstractmethod
    async def update_song_title(
        self,
        user_id: int,
        title: str,
        position: int,
    ) -> Optional[CollectionSongs]:
        pass

    @abstractmethod
    async def delete_songs(self, user_id: int, list_ids: List[int]) -> True:
        pass
