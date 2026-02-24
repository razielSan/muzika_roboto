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

    DELETE_IMAGE_FILE_ID: str = "AgACAgIAAxkBAAIJvGmFdN5orJwkcWn2wwv7J-2ALiaBAALzC2sbm8kwSKCgwqBOos5mAQADAgADeAADOAQ"
    DELETE_IMAGE_FILE_UNIQUE_ID: str = "AQAD8wtrG5vJMEh9"


settings: MainRouterSettings = MainRouterSettings()
