from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "admin.childes.del_user"
    MENU_REPLY_TEXT: str = "admin.childes.del_user" 
    MENU_CALLBACK_TEXT: str = "🗑 Удалить Пользователя"
    MENU_CALLBACK_DATA: str = "admin.childes.del_user"
    SHOW_IN_MAIN_MENU: bool = False
    NAME_FOR_LOG_FOLDER: str = "admin"
    NAME_FOR_TEMP_FOLDER: str = "admin/childes/del_user"
    ROOT_PACKAGE: str = "app.bot.modules.admin.childes.del_user"
    
settings: ModuleSettings = ModuleSettings()
    