from collections import defaultdict
import pkgutil
from typing import List
from pathlib import Path

from core.response.modules_loader import ModuleInfo
from core.contracts.constants import (
    DEFAULT_CHILD_SEPARATOR,
    DEFAULT_NAME_ROUTER,
    DEFAULT_NAME_SETTINGS,
)
from core.error_handlers.helpers import safe_import
from core.response.response_data import (
    Result,
    InlineKeyboardData,
    LoggingData,
)
from core.error_handlers.helpers import ok
from core.contracts.constants import DEFAULT_NAME_SETTINGS
from core.contracts.module import (
    DEFAULT_FIELD_FOR_INLINE_MENU_TEXT,
    DEFAULT_FIELD_FOR_INLINE_MENU_DATA,
)
from core.error_handlers.format import format_errors_message


def get_root_and_parent(
    module_name: str,
    root_package: str,
    separator: str = DEFAULT_CHILD_SEPARATOR,
) -> List[str]:
    """
    Проверка имени модуля на родительский и дочерний.

    Args:
        module_name (str): Имя модуля
        root_package: (str): Путь для импорта
        separator (str): Имя для связывыная дочернего и родительского модуля

    Returns:
        List[str]:

        Возвращает кортеж из двух параметров

        ("<root_module_name>", "<root_module_name>") - если модуль дочерний
        ("<root_module_name>", None) - если модуль) - если модуль корневой
    """

    relative = module_name.replace(root_package + ".", "")  # отсекаем
    # путь до модуля оставляя только имя - app.bot.modules.test -> test
    parts = relative.split(f".{separator}.")

    root = parts[0].split(".")[
        0
    ]  # отсекаем название файла если роутер корневой - test.router -> test
    parent = root if len(parts) > 1 else None
    return root, parent


def load_modules(
    root_package: str,
    name_settings: str = DEFAULT_NAME_SETTINGS,
    name_router: str = DEFAULT_NAME_ROUTER,
    separator: str = DEFAULT_CHILD_SEPARATOR,
) -> Result:
    """
    Проходится по модулям и возвращает обьект ModuleInfo c собранными
    данными

    Args:
        root_package (str): Путь для импорта, начинается с корневой директории

        Пример
        app.bot.modules

        name_settings (str): Имя файла для хранений настроек. По умолчанию DEFAULT_NAME_SETTINGS
        name_router (str): Имя файла для хранения роутера.По умолчанию DEFAULT_NAME_ROUTER

        separator (str): Имя для связывания дочернего и родительского модуля

        Имя папки для хранения дочерних модулей, формирования имен в settings,
        формирования имени роутера

    Returns:
        List[ModuleInfo]: обьект содержащий в себе

        Атрибуты ModuleInfo]:
            - package (str): Путь для импорта модуля
            - root (str): Имя корневого роутера
            - settings (ModuleType): Модуль с настройками
            - router (ModuleType): Модуль router
            - parent (str | None): Имя корневого роутера если дочерний если корневой то
            None

    """

    result_import = safe_import(module_package=root_package)
    if not result_import.ok:
        return result_import

    package = result_import.data

    modules = defaultdict(dict)

    for module_info in pkgutil.walk_packages(
        path=package.__path__, prefix=package.__name__ + "."
    ):
        module_name: str = module_info.name
        if not module_name.endswith(f"{name_settings}") and not module_name.endswith(
            f"{name_router}"
        ):
            continue
        root, parent = get_root_and_parent(
            module_name=module_name,
            root_package=root_package,
            separator=separator,
        )

        package_name, file_type = module_name.rsplit(".", 1)
        result_import = safe_import(module_package=module_name)

        if not result_import.ok:
            return result_import

        mod = result_import.data
        modules[package_name][file_type] = mod
        modules[package_name]["root"] = root
        modules[package_name]["parent"] = parent
        modules[package_name]["package"] = package_name
    array_modules = []
    for package, data in modules.items():
        if f"{name_settings}" not in data or f"{name_router}" not in data:
            continue  # дополнительная проверка

        array_modules.append(
            ModuleInfo(
                package=data.get("package"),
                root=data.get("root"),
                parent=data.get("parent"),
                router=data.get(f"{name_router}"),
                settings=data.get(f"{name_settings}"),
            )
        )
    return ok(data=array_modules)


def get_child_modules_settings_inline_data(
    module_path: Path,
    root_package: str,
    logging_data: LoggingData = None,
    name_settings: str = DEFAULT_NAME_SETTINGS,
    field_inline_data: str = DEFAULT_FIELD_FOR_INLINE_MENU_DATA,
    field_inline_text: str = DEFAULT_FIELD_FOR_INLINE_MENU_TEXT,
) -> List[InlineKeyboardData]:
    """
    Проходится по дочерним модулям из указанного пути по файлам settings.py.

    Записывает данные для инлайн клавиатуры в InlineKeyboardData.


    Args:
        module_path (Path): Путь до модуля
        root_package (str): Путь для импорта до childes, начинается с корневой директории

        Пример:
        app.bot.modules.example_modul.childes

        logging_data (LoggingData): Обьект класса LoggingData. По умолчанию Nont

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)

        name_settings (str): Имя файла для хранений настроек. По умолчанию DEFAULT_NAME_SETTINGS
        field_inline_data (str): Название поля в модели для обзначения callback инлайн клавиатуры
        aiogram
        field_inline_text (str): Название поля в модели для обозначения текста инлайн клавиатуры
        aiogram


    Returns:
        List[InlineKeyboardData]: Возвращает список из InlineKeyboardData

        Атрибуты InlineKeyboardData]:
                - text (str): Текст инлайн клавиатуры
                - callback_data (str): Callback_data инлайн клавиатуры
                - resize_keyboard (bool, Optional): Подгон размера клавиатуры. True по умолчанию
    """

    array_settings: List = []

    # Ищем по папкам внутри пути
    for path in module_path.iterdir():
        # Если не папка то пропускаем
        if not path.is_dir():
            continue

        # Если в папке есть settings.py
        settings_path: Path = path / f"{name_settings}.py"
        if settings_path.exists():
            rel_path: Path = settings_path.parent.relative_to(module_path)
            import_module: str = (
                f"{root_package}.{rel_path.as_posix().replace('/', '.')}"
            )
            module_settings_result = safe_import(
                module_package=f"{import_module}.{name_settings}",
                logging_data=logging_data,
            )

            if not module_settings_result.ok:
                logging_data.error_logger.error(
                    msg=format_errors_message(
                        name_router=logging_data.router_name,
                        function_name=get_child_modules_settings_inline_data.__name__,
                        error_text=f"Кнопка для {settings_path} не была "
                        f"создана - Ошибка при импорте модуля {module_path}",
                    )
                )

                continue

            module_settings = module_settings_result.data

            # Получаем settings из settings.py
            settings = getattr(module_settings, f"{name_settings}", None)

            # Проверка на присутвствие в settings полей для инлайн клавиатуры
            missing = {
                attr
                for attr in (field_inline_data, field_inline_text)
                if not hasattr(settings, attr)
            }
            if missing:
                logging_data.warning_logger.warning(
                    msg=f"{name_settings} {settings_path} пропущен, нет {missing}"
                )
                continue

            if (
                settings
                and hasattr(settings, f"{field_inline_data}")
                and hasattr(settings, f"{field_inline_text}")
            ):
                array_settings.append(
                    InlineKeyboardData(
                        text=settings.MENU_CALLBACK_TEXT,
                        callback_data=settings.MENU_CALLBACK_DATA,
                    )
                )
    return array_settings
