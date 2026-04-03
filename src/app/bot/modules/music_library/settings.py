from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "music_library"
    MENU_REPLY_TEXT: str = "music_library"
    MENU_CALLBACK_TEXT: str = "music_library"
    MENU_CALLBACK_DATA: str = "music_library"
    SHOW_IN_MAIN_MENU: bool = False
    NAME_FOR_LOG_FOLDER: str = "music_library"
    NAME_FOR_TEMP_FOLDER: str = "music_library"
    ROOT_PACKAGE: str = "app.bot.modules.music_library"
    MENU_IMAGE_FILE_ID: str = "AgACAgIAAxkBAAIFhmmAOwJQBKOpkNk4F94xdWjcF4NQAALnDGsb6LYAAUhZgLpnRetIFwEAAwIAA3kAAzgE"

    COLLECTION_SONGS_PHOTO_FILE_ID: str = "AgACAgIAAxkBAAKID2mdNxcQpN7sX4OvbwPXQMnrZy_9AAKJEmsbePvpSLvBWqeDeIdQAQADAgADeAADOgQ"
    COLLECTION_SONGS_PHOTO_FILE_UNIQUE_ID: str = "AQADiRJrG3j76Uh9"
    
    ADMIN_PANEL_PHOTO_FILE_ID: str = "AgACAgIAAxkBAAIHRGmBl3vdFd8Sb7Nh0dasuFYG1HtXAAJWEGsb6LYISDc5Cg0FAAFtpAEAAwIAA3kAAzgE"


settings: ModuleSettings = ModuleSettings()
