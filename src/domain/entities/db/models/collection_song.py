from dataclasses import dataclass


@dataclass
class CollectionSong:
    id: int
    title: str
    position: int
    file_id: str
    file_unique_id: str
    user_id: int
