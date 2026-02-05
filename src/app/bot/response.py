from dataclasses import dataclass
from pathlib import Path
from typing import Optional


@dataclass
class FomatAlbum:
    FORMAT_ALBUM: str = "(<year>) <name_album>"
    YEAR_OPEN: str = "("
    YEAR_CLOSE: str = ")"


format_album = FomatAlbum()
