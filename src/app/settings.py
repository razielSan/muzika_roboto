from pydantic import BaseModel


class AppSettings(BaseModel):
    """Общие настроцки для всего приложения."""

    SERVICE_NAME: str = "root_bot"
    NAME_FOR_LOG_FOLDER: str = "root_bot"


settings: AppSettings = AppSettings()
