from typing import Optional, List
from dataclasses import dataclass

from domain.entities.response import ExecutorSearchResponse


@dataclass
class UpdateAlbumYearData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    is_admin: bool
    year: None


@dataclass
class SearchExecutorData:
    executors: List[ExecutorSearchResponse]
    is_admin: bool
    search_executor: bool
    media: str
    caption: str
    name: None
    processing: None
