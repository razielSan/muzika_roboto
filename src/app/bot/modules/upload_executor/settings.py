from pydantic import BaseModel


class ModuleSettings(BaseModel):
    SERVICE_NAME: str = "upload_executor"
    MENU_REPLY_TEXT: str = "upload_executor" 
    MENU_CALLBACK_TEXT: str = "📥 Добавить Исполнителя в Библотеку"
    MENU_CALLBACK_DATA: str = "upload_executor"
    SHOW_IN_MAIN_MENU: bool = True
    NAME_FOR_LOG_FOLDER: str = "upload_executor"
    NAME_FOR_TEMP_FOLDER: str = "upload_executor"
    ROOT_PACKAGE: str = "app.bot.modules.upload_executor"
    
settings: ModuleSettings = ModuleSettings()
    