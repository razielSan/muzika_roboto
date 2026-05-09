from typing import List, Optional, Set
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
    ADMIN_MODE: str = "/start"
    LIST_BOT_COMMANDS: List[BotCommand] = [
        BotCommand(command="start", description="Запуск бота / Регистрация"),
        BotCommand(command="admin", description="Для администраторов"),
        BotCommand(command="music_library", description="Музыкальная библиотека"),
    ]
    ADMINS_LIST: List[str] = []

    ASYNC_SQLITE_BASE: str = f"sqlite+aiosqlite:///{DB_PATH}"
    SQLITE_BASE: str = f"sqlite:///{DB_PATH}"

    EXECUTOR_DEFAULT_PHOTO_FILE_ID: str = "AgACAgIAAxkBAAIBVml9nhC1Y0XMsk6-3evmf6yNyElJAAJIDGsbIWPwS4wwlY9A7yx9AQADAgADeQADOAQ"
    EXECUTOR_DEFAULT_PHOTO_UNIQUE_ID: str = "AQADSAxrGyFj8Et-"

    ALBUM_DEFAULT_PHOTO_FILE_ID: str = "AgACAgIAAxkBAAIBZ2l9oQn144OfNwEmtdJD6NVVbyFcAAJlDGsbIWPwS8FbQ1M2cbvAAQADAgADeQADOAQ"
    ALBUM_DEFAULT_PHOTO_UNIQUE_ID: str = "AQADZQxrGyFj8Et-"

    DELETE_IMAGE_FILE_ID: str = "AgACAgIAAxkBAAIJvGmFdN5orJwkcWn2wwv7J-2ALiaBAALzC2sbm8kwSKCgwqBOos5mAQADAgADeAADOAQ"
    DELETE_IMAGE_FILE_UNIQUE_ID: str = "AQAD8wtrG5vJMEh9"

    ADMIN_PANEL_PHOTO_FILE_ID: str = "AgACAgIAAxkBAAIHRGmBl3vdFd8Sb7Nh0dasuFYG1HtXAAJWEGsb6LYISDc5Cg0FAAFtpAEAAwIAA3kAAzgE"

    AUDIO_EXTENSIONS: Set[str] = {".mp3", ".flac", ".wav", ".ogg", ".m4a"}
    MUSICL_LIBRARY_MODULE_NAME: str = "music_library"

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )


class ProxySettings(BaseSettings):

    BOT_DIR: Path = Path(__file__).resolve().parent

    WEBSHARE_LOGIN: Optional[str] = None
    WEBSHARE_PASSWORD: Optional[str] = None
    WEBSHARE_HOST: Optional[str] = None
    WEBSHARE_PORT: Optional[str] = None

    USE_WEBSHARE_PROXY: bool = False
    USE_OTHER_PROXY: bool = False

    OTHER_HOST: Optional[str] = None
    OTHER_PORT: Optional[str] = None

    def get_proxy_url(self):
        if self.USE_WEBSHARE_PROXY:
            return (
                f"http://{self.WEBSHARE_LOGIN}:{self.WEBSHARE_PASSWORD}"
                f"@{self.WEBSHARE_HOST}:{self.WEBSHARE_PORT}"
            )
        if self.USE_OTHER_PROXY:
            return f"http://{self.OTHER_HOST}:{self.OTHER_PORT}"
        return None

    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )


proxy_settings = ProxySettings()
settings = BotSettings()
