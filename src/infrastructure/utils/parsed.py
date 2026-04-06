from pathlib import Path
from typing import List

from domain.entities.response import AlbumParsedResponse
from infrastructure.aiogram.response import format_album


def parse_album(base_path: Path) -> List[AlbumParsedResponse]:
    albums: List[AlbumParsedResponse] = []
    for album_dir in base_path.iterdir():
        year, title = album_dir.stem.strip(format_album.YEAR_OPEN).split(
            format_album.YEAR_CLOSE
        )
        title: str = title.strip(" +-,.")
        albums.append(AlbumParsedResponse(title=title, year=int(year), path=album_dir))
    return albums
