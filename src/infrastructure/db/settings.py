from dataclasses import dataclass

from pathlib import Path


@dataclass
class DataBaseSettings:
    SRC_DIR: Path = Path(__file__).resolve().parent.parent.parent
    DATABASE_DIR: Path = SRC_DIR / "app" / "bot" / "data" / "music_play.db"

    ASYNC_SQLITE_BASE: str = f"sqlite+aiosqlite:///{DATABASE_DIR}"
    SQLITE_BASE: str = f"sqlite:///{DATABASE_DIR}"


data_base_settings = DataBaseSettings()
