from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "admin.childes.photo_info"
    MENU_REPLY_TEXT: str = "admin.childes.photo_info" 
    MENU_CALLBACK_TEXT: str = "Узнать file_id photo"
    MENU_CALLBACK_DATA: str = "admin.childes.photo_info"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "admin"
    NAME_FOR_TEMP_FOLDER: str = "admin/childes/photo_info"
    ROOT_PACKAGE: str = "app.bot.modules.admin.childes.photo_info"
    
settings: ModuleSettings = ModuleSettings()
    