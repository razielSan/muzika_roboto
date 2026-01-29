from dataclasses import dataclass


@dataclass
class SongResponse:
    file_id: str
    title: str
