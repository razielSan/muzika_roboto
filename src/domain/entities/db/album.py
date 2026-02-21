from dataclasses import dataclass


@dataclass
class Album:
    id: int
    title: str
    year: int
    photo_file_id: str
    photo_file_unique_id: str
    executor_id: int
