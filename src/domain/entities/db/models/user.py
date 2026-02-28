from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    id: int
    name: str
    telegram: int
    collection_songs_photo_file_id: Optional[str] = None
    collection_songs_photo_file_unique_id: Optional[str] = None
