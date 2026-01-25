from typing import List, Optional
from pathlib import Path

from aiogram.types import BotCommand
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotSettings(BaseSettings):
    """Общие настройки бота."""

    SERVICE_NAME: str = "bot"
    NAME_FOR_LOG_FOLDER: str = "bot"

    TOKEN: Optional[str] = None
    LIST_BOT_COMMANDS: List[BotCommand] = [
        BotCommand(command="start", description="Меню бота")
    ]

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent / ".env", extra="ignore"
    )


settings = BotSettings()
