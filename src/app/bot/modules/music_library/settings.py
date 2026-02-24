from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "music_library"
    MENU_REPLY_TEXT: str = "music_library"
    MENU_CALLBACK_TEXT: str = "music_library"
    MENU_CALLBACK_DATA: str = "music_library"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "music_library"
    NAME_FOR_TEMP_FOLDER: str = "music_library"
    ROOT_PACKAGE: str = "app.bot.modules.music_library"
    MENU_IMAGE_FILE_ID: str = "AgACAgIAAxkBAAIFhmmAOwJQBKOpkNk4F94xdWjcF4NQAALnDGsb6LYAAUhZgLpnRetIFwEAAwIAA3kAAzgE"

settings: ModuleSettings = ModuleSettings()
