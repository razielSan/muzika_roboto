from pathlib import Path

from app.core.paths import app_path


class BotPath:
    BOT_DIR: Path = app_path.APP_DIR / "bot"
    STATIC_DIR: Path = BOT_DIR / "static"
    TEMP_DIR: Path = BOT_DIR / "temp"
    LOG_DIR: Path = BOT_DIR / "logs"


bot_path = BotPath()
