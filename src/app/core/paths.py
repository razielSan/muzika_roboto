from pathlib import Path
from dataclasses import dataclass

from core.paths.paths import SRC_DIR


@dataclass
class AppPath:
    APP_DIR: Path = SRC_DIR / "app"
    LOG_DIR: Path = APP_DIR / "logs"
    STATIC_DIR: Path = APP_DIR / "static"
    TEMP_DIR: Path = APP_DIR / "temp"


app_path: AppPath = AppPath()
