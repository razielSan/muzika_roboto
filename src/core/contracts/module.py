from typing import Protocol
from enum import Enum


class ModuleSettingsContract(Protocol):
    # Идентификатор модуля (уникальный)
    SERVICE_NAME: str

    # Где лежит код
    ROOT_PACKAGE: str

    # Флаг проверки для подключения корневого модуля к главному меню
    SHOW_IN_MAIN_MENU: bool

    # FS
    NAME_FOR_TEMP_FOLDER: str
    NAME_FOR_LOG_FOLDER: str

    MENU_REPLY_TEXT: str
    SHOW_IN_MAIN_MENU: bool
    MENU_CALLBACK_TEXT: str
    MENU_CALLBACK_DATA: str


DEFAULT_FIELD_FOR_INLINE_MENU_DATA: str = "MENU_CALLBACK_DATA"
DEFAULT_FIELD_FOR_INLINE_MENU_TEXT: str = "MENU_CALLBACK_TEXT"

REQUIRED_FIELDS_MODULES = {
    "SERVICE_NAME",
    "ROOT_PACKAGE",
    "NAME_FOR_TEMP_FOLDER",
    "NAME_FOR_LOG_FOLDER",
    "SHOW_IN_MAIN_MENU",
    "MENU_CALLBACK_TEXT",
    "MENU_CALLBACK_DATA",
    "MENU_REPLY_TEXT",
}


REQUIRED_FIELD_APP_MODULES_SETTINGS = {
    "SERVICE_NAME",
    "NAME_FOR_LOG_FOLDER",
}

REQUIRED_FIELD_BOT_MODULES_SETTINGS = {
    "SERVICE_NAME",
    "NAME_FOR_LOG_FOLDER",
    "TOKEN",
    "LIST_BOT_COMMANDS",
}


class RequiredFieldsModulSettings(Enum):
    SERVICE_NAME: str = "SERVICE_NAME"
    MENU_REPLY_TEXT: str = "MENU_REPLY_TEXT"
    MENU_CALLBACK_TEXT: str = "MENU_CALLBACK_TEXT"
    MENU_CALLBACK_DATA: str = "MENU_CALLBACK_DATA"
    SHOW_IN_MAIN_MENU: bool = "SHOW_IN_MAIN_MENU"
    NAME_FOR_LOG_FOLDER: str = "NAME_FOR_LOG_FOLDER"
    NAME_FOR_TEMP_FOLDER: str = "NAME_FOR_TEMP_FOLDER"
    ROOT_PACKAGE: str = "ROOT_PACKAGE"

    @classmethod
    def get_fields(cls):
        return {
            cls.SERVICE_NAME.name: cls.SERVICE_NAME.value,
            cls.MENU_REPLY_TEXT.name: cls.MENU_REPLY_TEXT.value,
            cls.MENU_CALLBACK_TEXT.name: cls.MENU_CALLBACK_TEXT.value,
            cls.MENU_CALLBACK_DATA.name: cls.MENU_CALLBACK_DATA.value,
            cls.SHOW_IN_MAIN_MENU.name: cls.SHOW_IN_MAIN_MENU.value,
            cls.NAME_FOR_LOG_FOLDER.name: cls.NAME_FOR_LOG_FOLDER.value,
            cls.NAME_FOR_TEMP_FOLDER.name: cls.NAME_FOR_TEMP_FOLDER.value,
            cls.ROOT_PACKAGE.name: cls.ROOT_PACKAGE.value,
        }
