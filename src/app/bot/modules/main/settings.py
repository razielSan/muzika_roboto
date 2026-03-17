from pydantic import BaseModel


class MainRouterSettings(BaseModel):
    """Модель для главного меню."""

    SERVICE_NAME: str = "main"
    MENU_REPLY_TEXT: str = "main"
    MENU_CALLBACK_TEXT: str = "main"
    MENU_CALLBACK_DATA: str = "main"
    SHOW_IN_MAIN_MENU: bool = False
    NAME_FOR_TEMP_FOLDER: str = "main"
    NAME_FOR_LOG_FOLDER: str = "main"
    ROOT_PACKAGE: str = "app.bot.modules.main"


settings: MainRouterSettings = MainRouterSettings()
