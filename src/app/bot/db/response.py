from dataclasses import dataclass


@dataclass
class SongResponse:
    file_id: str
    file_unique_id: str
    title: str
    position: int