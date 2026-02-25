from dataclasses import dataclass


@dataclass
class CollectionSongResponse:
    file_id: str
    file_unique_id: str
    title: str
