from pathlib import Path
import importlib
from typing import Protocol, List, Optional
from dataclasses import dataclass
import pkgutil
from types import ModuleType


from core.contracts.constants import (
    DEFAULT_CHILD_SEPARATOR,
    DEFAULT_BOT_MODULES_ROOT,
)
from core.logging.factory import LoggerFactory
from core.logging.storage import storage
from core.logging.runtime import LoggerRuntime
from core.logging.format import log_format
from core.module_loader.runtime.validate import validate_module
from core.contracts.module import (
    REQUIRED_FIELD_APP_MODULES_SETTINGS,
    REQUIRED_FIELD_BOT_MODULES_SETTINGS,
    REQUIRED_FIELDS_MODULES,
)
from core.contracts.constants import (
    DEFAULT_NAME_SETTINGS,
    DEFAUTL_NAME_APP_PATH,
    DEFAUTL_NAME_BOT_PATH,
)


class BotPathProtocol(Protocol):
    BOT_DIR: Path
    TEMP_DIR: Path
    LOG_DIR: Path
    STATIC_DIR: Path


class AppPathProtocol(Protocol):
    APP_DIR: Path
    TEMP_DIR: Path
    LOG_DIR: Path
    STATIC_DIR: Path


class AppSettingsProtocol(Protocol):
    SERVICE_NAME: str
    NAME_FOR_LOG_FOLDER: str


class BotSettingsProtocol(Protocol):
    SERVICE_NAME: str
    NAME_FOR_LOG_FOLDER: str
    TOKEN: str
    LIST_BOT_COMMANDS: List


class ModuleSettings(Protocol):
    SERVICE_NAME: str
    MENU_REPLY_TEXT: str
    MENU_CALLBACK_TEXT: str
    MENU_CALLBACK_DATA: str
    NAME_FOR_LOG_FOLDER: str
    NAME_FOR_TEMP_FOLDER: str
    ROOT_PACKAGE: str


@dataclass
class AppContext:
    app_path: AppPathProtocol
    bot_path: BotPathProtocol
    app_settings: AppSettingsProtocol
    bot_settings: BotSettingsProtocol
    loggers: LoggerRuntime
    root_modules_settings: List[ModuleSettings]


def load_bot_paths(
    bot_core: str,
    name_variable: str = "bot_path",
) -> BotPathProtocol:
    """
    Возвращает обьект хранящий путь для бота.

    Args:
        bot_core (str): Путь до модуля, в котором хранятся пути для бота

        Пример:
        app.bot.core.paths

        name_variable (str): Имя переменной хранения путей бота

    Raises:
        RuntimeError: Ошибка если переменная не найдена

    Returns:
        BotPath: содержит в себе

        атрибуты BotPath:
            - BOT_DIR  (Path)
            - TEMP_DIR (Path)
            - LOG_DIR  (Path)
            - STATIC_DIR (Path)
    """
    module: ModuleType = importlib.import_module(bot_core)
    if not hasattr(module, name_variable):
        raise RuntimeError(f"{name_variable} not found")
    return module.bot_path


def load_app_paths(
    app_core: str,
    name_variable: str = "app_path",
) -> AppPathProtocol:
    """
    Возвращает обьект хранящий путь для приложения.

    Args:
        app_core (str): Путь до модуля, в котором хранятся пути для приложения

        Пример:
        app.core.paths

        name_variable (str): Имя переменной хранения путей приложения.

    Raises:
        RuntimeError: Ошибка если переменная не найдена

    Returns:
       AppPath: содержит в себе

        атрибуты AppPath:
            - APP_DIR  (Path)
            - TEMP_DIR (Path)
            - LOG_DIR  (Path)
            - STATIC_DIR (Path)
    """
    module: ModuleType = importlib.import_module(app_core)
    if not hasattr(module, name_variable):
        raise RuntimeError(f"{name_variable} not found")
    return module.app_path


def load_data_modules(
    core: str,
    requiered_fields: set,
    name: Optional[str] = None,
    default_name_object: str = "settings",
) -> object:
    """
    Возвращает именнованый обьект из модуля.
    Обьект должен быть классом для проверки полей.

    Args:
        core (str): Путь до модуля в котором хранятся настройки

        Пример:
        app.bot.core.settings

        requiered_fields (set): Поля для проверки
        name (Optinal, str): Имя обьекта.Если не передано будет использовано default_name_object
        default_name_object (str): Дефолтное имя для обьекта


    Raises:
        RuntimeError: Ошибка если переменная не найдена

    Returns:
        object: Класс

    """
    name = name if name else default_name_object

    settings = validate_module(
        root_package=core, required_field_modules=requiered_fields, name=name
    )
    if not settings.ok:
        raise RuntimeError(settings.error.message)

    return settings.data


def load_bot_root_modules_data(
    root_package: str,
    file_name: str,
    separator: str = DEFAULT_CHILD_SEPARATOR,
) -> List[ModuleSettings]:
    """
    Возвращает список из именнованных обьектов содержащих настройки для корневых модулей.

    Args:
        root_package (str): Путь для модуля, в котором хранятся модули

        Пример:
        app.bot.modules

        file_name (str): Имя обьекта
        separator: (str): Имя для связывыния дочернего и родительского модуля.
        По умолчанию DEFAULT_CHILD_SEPARATOR

        Имя папки для хранения дочерних модулей, формирования имен в settings,

    Returns:
        List[ModuleSettings]: содержит в себе

        атрибуты ModuleSettings:
            - SERVICE_NAME (str)
            - MENU_REPLY_TEXT (str)
            - MENU_CALLBACK_TEXT (str)
            - MENU_CALLBACK_DATA (str)
            - SHOW_IN_MAIN_MENU
            - NAME_FOR_LOG_FOLDER (str)
            - NAME_FOR_TEMP_FOLDER: (str)
            - ROOT_PACKAGE: (str)

    """
    package: ModuleType = importlib.import_module(root_package)  # получаем модуль
    array_settings: List = []  # список для настроек
    for module_info in pkgutil.walk_packages(
        path=package.__path__,
        prefix=package.__name__ + ".",
    ):  # проходимся по пакетам модуля
        name: str = module_info.name

        if not name.endswith(f"{file_name}"):  # если не нужный файл
            continue

        if separator in name:  # если дочерний то пропускаем итерацию
            continue

        settings = validate_module(
            root_package=name,
            required_field_modules=REQUIRED_FIELDS_MODULES,
            name=file_name,
            root=True,
        )
        if not settings.ok:
            raise RuntimeError(settings.error.message)

        array_settings.append(settings.data)
    return array_settings


def init_logging(
    app_path: AppPathProtocol,
    bot_path: BotPathProtocol,
    app_settings: object,
    bot_settings: object,
    root_modules_settings: List[ModuleSettings],
) -> LoggerRuntime:
    """
    Ининициализирует логи.

    Возвращат обьект содержий в себе проинициализированные логи

    Args:
        app_path (AppPathProtocol): Обьект содержащий пути для приложения
        bot_path (BotPathProtocol): Обьект содержащий пути для бота
        app_settings (object): Обьект содержащий настройки для приложения
        bot_settings (object): Обьект содержащий настройки для бота
        root_modules_settings (List[ModuleSettings]): Список состоящий из обьектов
        содержащих настройки для модулей

    Returns:
        LoggerRuntime: Склад логов
    """
    # Создание фабрики логгеров для приложения и бота
    app_factory: LoggerFactory = LoggerFactory(
        base_path=app_path.LOG_DIR,
        datefmt=log_format.DATE_FORMAT,
        format_log=log_format.LOG_FORMAT,
    )

    bot_factory: LoggerFactory = LoggerFactory(
        base_path=bot_path.LOG_DIR,
        datefmt=log_format.DATE_FORMAT,
        format_log=log_format.LOG_FORMAT,
    )

    # Добавление в хранилище фабрики логгеров логгеры бота, приложения,
    # корневых модулей

    storage.add(
        name=app_settings.NAME_FOR_LOG_FOLDER,
        data=app_factory.create(name=app_settings.NAME_FOR_LOG_FOLDER),
    )
    storage.add(
        name=bot_settings.NAME_FOR_LOG_FOLDER,
        data=bot_factory.create(name=bot_settings.NAME_FOR_LOG_FOLDER),
    )
    for settings in root_modules_settings:
        storage.add(
            name=settings.NAME_FOR_LOG_FOLDER,
            data=bot_factory.create(
                name=settings.NAME_FOR_LOG_FOLDER,
                subdir=settings.NAME_FOR_LOG_FOLDER,
            ),
        )

    LoggerRuntime.init(storage=storage)
    return LoggerRuntime


def create_app_context(
    bot_modules_root: str = DEFAULT_BOT_MODULES_ROOT,
) -> AppContext:
    """Создает контекст приложения."""

    app_settings = load_data_modules(
        core="app",
        requiered_fields=REQUIRED_FIELD_APP_MODULES_SETTINGS,
    )
    bot_settings = load_data_modules(
        core="app.bot",
        requiered_fields=REQUIRED_FIELD_BOT_MODULES_SETTINGS,
    )
    app_path = load_app_paths(
        "app.core.paths",
        name_variable=DEFAUTL_NAME_APP_PATH,
    )
    bot_path = load_bot_paths(
        "app.bot.core.paths",
        name_variable=DEFAUTL_NAME_BOT_PATH,
    )
    modules_settings = load_bot_root_modules_data(
        root_package=bot_modules_root,
        file_name=DEFAULT_NAME_SETTINGS,
    )

    loggers = init_logging(
        app_path=app_path,
        app_settings=app_settings,
        bot_path=bot_path,
        bot_settings=bot_settings,
        root_modules_settings=modules_settings,
    )
    return AppContext(
        app_path=app_path,
        bot_path=bot_path,
        app_settings=app_settings,
        bot_settings=bot_settings,
        loggers=loggers,
        root_modules_settings=modules_settings,
    )
