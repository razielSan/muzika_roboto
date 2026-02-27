from dataclasses import dataclass
from typing import Optional, List


@dataclass
class CollectionSongResponse:
    file_id: str
    file_unique_id: str
    title: str
    position: Optional[int] = None


@dataclass
class UserCollectionSongResponse:
    collection_songs: List[CollectionSongResponse]
    collection_song_photo_unique_id: Optional[str] = None
    collection_song_photo_file_id: Optional[str] = None
