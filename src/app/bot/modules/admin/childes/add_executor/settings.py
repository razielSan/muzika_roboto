from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "admin.childes.add_executor"
    MENU_REPLY_TEXT: str = "admin.childes.add_executor" 
    MENU_CALLBACK_TEXT: str = "📥 Загрузить Исполнителя"
    MENU_CALLBACK_DATA: str = "admin.childes.add_executor"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "admin"
    NAME_FOR_TEMP_FOLDER: str = "admin/childes/add_executor"
    ROOT_PACKAGE: str = "app.bot.modules.admin.childes.add_executor"
    
settings: ModuleSettings = ModuleSettings()
    