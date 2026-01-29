from typing import List, Optional
from pathlib import Path

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Общие настройки бота."""

    BOT_DIR: Path = Path(__file__).resolve().parent
    DB_PATH: Path = BOT_DIR / "data" / "music_play.db"

    SERVICE_NAME: str = "bot"
    NAME_FOR_LOG_FOLDER: str = "bot"

    TOKEN: Optional[str] = None
    LIST_BOT_COMMANDS: List[BotCommand] = [
        BotCommand(command="start", description="Меню бота")
    ]
    
    ASYNC_SQLITE_BASE: str = f"sqlite+aiosqlite:///{DB_PATH}"
    SQLITE_BASE: str = f"sqlite:///{DB_PATH}"

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=BOT_DIR / ".env", extra="ignore"
    )


settings = BotSettings()
