from typing import List
from pathlib import Path

from app.bot.view_model import AlbumResponse


class ApiAddExecutorAPI:
    def parse_album(self, base_path: Path) -> List[AlbumResponse]:
        albums = []
        for album_dir in base_path.iterdir():
            year, title = album_dir.stem.strip("(").split(")")
            title = title.strip().lower()
            albums.append(AlbumResponse(title=title, year=int(year), path=album_dir))
        return albums


add_executor_api: ApiAddExecutorAPI = ApiAddExecutorAPI()
