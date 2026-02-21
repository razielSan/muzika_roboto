from dataclasses import dataclass
from typing import Optional


@dataclass
class Executor:
    id: int
    name: str
    country: str
    photo_file_id: str
    photo_file_unique_id: str
    user_id: Optional[int]
    
    @property
    def is_global(self):
        return self.user_id is None

