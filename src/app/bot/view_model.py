from pathlib import Path
from typing import Optional
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


@dataclass
class SongResponse:
    file_id: Optional[str] = None
    file_unique_id: Optional[str] = None
    title: Optional[str] = None
    position: Optional[int] = None
    album_id: Optional[int] = None
    album_photo_file_id: Optional[str] = None
    album_title: Optional[str] = None
    album_year: Optional[int] = None
    album_executor_id: Optional[int] = None
    info_album: Optional[str] = None
