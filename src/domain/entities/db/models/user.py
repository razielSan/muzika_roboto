from dataclasses import dataclass
from typing import Optional, List

from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.db.models.collection_songs import (
    CollectionSongs as CollectionSongsDomain,
)


@dataclass
class User:
    id: int
    name: str
    telegram: int
    library_executors: Optional[List[ExecutorDomain]] = None
    executors: Optional[List[ExecutorDomain]] = None
    collection_songs: Optional[List[CollectionSongsDomain]] = None
    collection_songs_photo_file_id: Optional[str] = None
    collection_songs_photo_file_unique_id: Optional[str] = None
