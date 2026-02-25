from typing import Sequence
from abc import ABC, abstractmethod

from domain.entities.db.models.collection_song import CollectionSong


class CollectionSongRepository(ABC):
    @abstractmethod
    async def get_all_songs(
        self,
        user_id: int,
    ) -> Sequence[CollectionSong]:
        pass
