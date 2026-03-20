from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class SongResponse:
    title: str
    file_id: str
    file_unique_id: str
    id: Optional[int] = None
    album_id: Optional[int] = None
    position: Optional[int] = None


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
    current_user_id: Optional[int]  # user_id пользователя для скроллинга
    is_global: Optional[
        bool
    ]  # для определения глобальный или пользовательский исполнитель
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
