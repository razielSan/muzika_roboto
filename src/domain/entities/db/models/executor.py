from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Executor:
    id: int
    name: str
    country: str
    photo_file_id: str
    photo_file_unique_id: str
    name_lower: Optional[str]
    user_id: Optional[int] = None
    albums: Optional[List] = None
    genres: Optional[List] = None
