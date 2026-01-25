from types import ModuleType

from core.contracts.constants import (
    DEFAULT_NAME_SETTINGS,
)
from core.contracts.module import REQUIRED_FIELDS_MODULES
from core.response.response_data import Result
from core.error_handlers.helpers import ok, fail
from core.error_handlers.helpers import safe_import


def validate_module(
    root_package: str,
    required_field_modules: set = REQUIRED_FIELDS_MODULES,
    name: str = DEFAULT_NAME_SETTINGS,
    root: bool = False,
) -> Result:
    """
    Ипортирует именновыный модуль и проверяет его поля.
    Обьект должен быть классом для проверки полей.

    Args:
        root_package (str): Путь для модуля, в котором хранится модуль

        Пример:

        root=True
        app.bot.modules.settings.settings

        root=False
        app.bot.modules.settings

        required_field_modules (set, optional): Поля для проверки.
        name (str, optional): Имя обьекта По умолчанию Defaults to DEFAULT_NAME_SETTINGS.
        root (bool, optional): Флаг для проверки. Если True то импортирует сразу root_package,
        если False то подставляет name

    Returns:
        Result: содержит в себе

        атрибуты Result:
            - ok (bool)
            - data (Optional[Any])
            - error: (Optional[Error])

        атрибуты Error:
            - code (str)
            - message (str)
            - detatails (Optional[Any])
    """

    result_import = None
    if root:
        result_import: Result = safe_import(module_package=f"{root_package}")
    else:
        result_import: Result = safe_import(module_package=f"{root_package}.{name}")

    if not result_import.ok:
        return result_import

    module_data: ModuleType = result_import.data

    if not hasattr(module_data, name):
        return fail(code="Invalide module", message=f"{name} not found - {module_data}")

    response_data = getattr(module_data, f"{name}")

    modules_set = set(
        response_data.model_fields.keys()
    )  # получаем множество из имен полей модели
    result_data = required_field_modules.difference(modules_set)
    if result_data:  # если осталось хоть одно поле значит его нет в загруженной модели
        return fail(
            code="Invalide module",
            message=f"Invalide module settings : {result_data} missing",
        )

    return ok(data=response_data)
