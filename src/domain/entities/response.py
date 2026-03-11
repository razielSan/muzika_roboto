from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class SongResponse:
    id: int
    title: str
    position: int
    file_id: str
    file_unique_id: str
    album_id: int


@dataclass
class AlbumResponse:
    id: int
    executor_id: int
    year: int
    title: str


@dataclass
class AlbumPageResponse:
    id: int
    user_id: Optional[int]
    executor_id: int
    year: int
    title: int
    photo_file_id: str
    photo_file_unique_id: str
    current_page_executor: int
    album_position: int
    songs: List[SongResponse]


@dataclass
class ExecutorPageResponse:
    id: int
    user_id: Optional[int]
    name: str
    country: str
    photo_file_id: int
    photo_file_unique_id: int
    current_page: int
    total_pages: int
    albums: List[AlbumResponse]
    genres: List[str]


@dataclass
class CollectionSongsResponse:
    file_id: str
    file_unique_id: str
    title: str
    position: Optional[int] = None
    id: Optional[int] = None


@dataclass
class UserCollectionSongsResponse:
    collection_songs: Union[List[CollectionSongsResponse], List]
    collection_songs_photo_file_id: Optional[str] = None
    collection_songs_photo_file_unique_id: Optional[str] = None
