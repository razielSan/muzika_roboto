from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "admin.childes.base_music"
    MENU_REPLY_TEXT: str = "admin.childes.base_music" 
    MENU_CALLBACK_TEXT: str = "📻 Общая Музыкальная Коллекция"
    MENU_CALLBACK_DATA: str = "admin.childes.base_music"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "admin"
    NAME_FOR_TEMP_FOLDER: str = "admin/childes/base_music"
    ROOT_PACKAGE: str = "app.bot.modules.admin.childes.base_music"
    
settings: ModuleSettings = ModuleSettings()
    