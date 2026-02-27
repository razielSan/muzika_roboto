from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "music_library.childes.collection_of_songs"
    MENU_REPLY_TEXT: str = "music_library.childes.collection_of_songs"
    MENU_CALLBACK_TEXT: str = "🎧 Мой Сборник Песен"
    MENU_CALLBACK_DATA: str = "music_library.childes.collection_of_songs"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "music_library"
    NAME_FOR_TEMP_FOLDER: str = "music_library/childes/collection_of_songs"
    ROOT_PACKAGE: str = "app.bot.modules.music_library.childes.collection_of_songs"


settings: ModuleSettings = ModuleSettings()
