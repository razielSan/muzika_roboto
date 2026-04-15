from typing import Optional
from dataclasses import dataclass


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
