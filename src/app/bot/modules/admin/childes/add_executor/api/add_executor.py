from typing import List

from pathlib import Path
from dataclasses import dataclass


@dataclass
class ParsedAlbum:
    title: str
    year: int
    path: Path

    @classmethod
    def validate(cls):
        return f"{cls.year} {cls.title}"


class ApiAddExecutor:
    def parse_album(self, base_path: Path) -> List[ParsedAlbum]:
        albums = []
        for album_dir in base_path.iterdir():
            year, title = album_dir.stem.strip("(").split(")")
            albums.append(ParsedAlbum(title=title, year=int(year), path=album_dir))
        return albums


api_add_executor: ApiAddExecutor = ApiAddExecutor()
