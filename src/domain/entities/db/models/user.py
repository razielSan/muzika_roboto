from dataclasses import dataclass
from typing import Optional, List

from domain.entities.db.models.executor import Executor as ExecutorDomain


@dataclass
class User:
    id: int
    name: str
    telegram: int
    library_executors: Optional[List[ExecutorDomain]] = None
    collection_songs_photo_file_id: Optional[str] = None
    collection_songs_photo_file_unique_id: Optional[str] = None
