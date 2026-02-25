from dataclasses import dataclass


@dataclass
class CollectionSong:
    id: int
    title: str
    position: int
    photo_file_id: str
    photo_file_unique_id: str
    file_id: str
    file_unique_id: str
    user_id: int
