from pathlib import Path
from typing import Optional, List
from dataclasses import dataclass


@dataclass
class AlbumResponse:
    title: str
    year: int
    info_executor: Optional[str] = None
    executor_id: Optional[int] = None
    executor_photo_file_id: Optional[str] = None
    album_id: Optional[int] = None
    path: Optional[Path] = None
    count_executors: Optional[int] = None


@dataclass
class ExecutorResponse:
    info_executor: str
    executor_id: int
    photo_file_id: str


@dataclass
class ExecutorPageRepsonse:
    executor: ExecutorResponse
    albums: List[AlbumResponse]
    total_pages: int
    current_page: int


@dataclass
class SongResponse:
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None
    song_id: Optional[int] = None
    title: Optional[str] = None
    position: Optional[int] = None
    album_id: Optional[int] = None
    album_photo_file_id: Optional[str] = None
    album_title: Optional[str] = None
    album_year: Optional[int] = None
    album_executor_id: Optional[int] = None
    info_album: Optional[str] = None
