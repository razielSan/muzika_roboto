from dataclasses import dataclass


@dataclass
class Song:
    id: int
    title: str
    position: int
    file_id: str
    file_unique_id: str
    album_id: int
