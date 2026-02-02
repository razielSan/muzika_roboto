from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "admin"
    MENU_REPLY_TEXT: str = "admin" 
    MENU_CALLBACK_TEXT: str = "admin"
    MENU_CALLBACK_DATA: str = "admin"
    SHOW_IN_MAIN_MENU: bool = False
    NAME_FOR_LOG_FOLDER: str = "admin"
    NAME_FOR_TEMP_FOLDER: str = "admin"
    ROOT_PACKAGE: str = "app.bot.modules.admin"
    
settings: ModuleSettings = ModuleSettings()
    