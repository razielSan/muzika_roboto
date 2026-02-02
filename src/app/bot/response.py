from dataclasses import dataclass


@dataclass
class FomatAlbum:
    FORMAT_ALBUM: str = "(<year>) <name_album>"
    YEAR_OPEN: str = "("
    YEAR_CLOSE: str = ")"


format_album = FomatAlbum()
