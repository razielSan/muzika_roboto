from dataclasses import dataclass
from typing import Optional


@dataclass
class CollectionSong:
    id: int
    title: str
    position: str
    file_id: str
    file_unique_id: str
    user_id: Optional[int]
