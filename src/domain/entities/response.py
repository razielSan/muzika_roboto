from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CollectionSongsResponse:
    file_id: str
    file_unique_id: str
    title: str
    position: Optional[int] = None


@dataclass
class UserCollectionSongsResponse:
    collection_songs: List[CollectionSongsResponse]
    collection_songs_photo_file_id: Optional[str] = None
    collection_songs_photo_file_unique_id: Optional[str] = None
