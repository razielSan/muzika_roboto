from pathlib import Path

from typing import Dict, List
from pathlib import Path

from core.response.response_data import Result
from core.error_handlers.helpers import ok, fail
from core.contracts.constants import (
    DEFAULT_CHILD_SEPARATOR,
    DEFAULT_NAME_OF_THE_ROUTER_FOLDER,
    DEFAULT_NAME_SETTINGS,
    RESERVED_NAMES,
)
from core.contracts.templates import TEMPLATE_DIRS, TEMPLATE_FILES
from core.contracts.module import REQUIRED_FIELDS_MODULES
from core.module_loader.scaffolding.validate import (
    validate_module_settings_file,
    validate_module_structure,
)
from core.utils.filesistem import save_delete_data
from core.contracts.module import RequiredFieldsModulSettings


def generate_content(template: str, **kwargs):
    """
    Подставляет значения в строке на переданные.
    """

    for key, value in kwargs.items():
        template = template.replace(f"{{{key}}}", value)
    return template


def create_module(
    root_dir: Path,
    root_package: str,
    module_name: str,
    name_router_folders: str = DEFAULT_NAME_OF_THE_ROUTER_FOLDER,
    separator: str = DEFAULT_CHILD_SEPARATOR,
    template_dirs: Dict = TEMPLATE_DIRS,
    template_files: Dict = TEMPLATE_FILES,
    requiered_field_modul: RequiredFieldsModulSettings = RequiredFieldsModulSettings,
    reservied_names: set = RESERVED_NAMES,
) -> Result:
    """
    Создает модуль и все вложенные модули

    Дочерние модули будут разделены

    Архитектура модуля:

    api/
    fsm/
    services/
    utils/
    keyboards/
    childes/
    handlers/
    __init__.py
    extensions.py
    router.py
    settings.py
    response.py

    Args:
        root_dir (Path): Путь до корневой директории проекта
        root_package: (str): Путь для импорта, начинается с корневой директории

        Пример
        app.bot.modules

        module_name: Имя модуля.Дочение модули разделяются "."

        Пример
        test.test

        separator: (str): Имя для связывыния дочернего и родительского модуля

        Имя папки для хранения дочерних модулей, формирования имен в settings,
        формирования имени роутера

        template_dirs: (Dict): Шаблон с директориями для создания модуля
        template_files: (Dict): Шаблон с файлами для создания модуля
        requiered_field_modul: (RequiredFieldsModulSettings): Еnum для подставления в
        шаблон в имена полей settings.

    Returns:
        Result: содержит в себе

        атрибуты Result:
            - ok (bool)
            - data (Optional[Any])
            - error: (Optional[Error])

        атрибуты Error:
            - code (str)
            - message (str)
            - details (Optional[Any])
    """
    list_modules: List[str] = module_name.split(".")  # разделяем имя модуля для
    # создания родетельских и дочерних модулей

    # Полный путь до конечного дочернего модуля, для проверки на его повторное создание
    full_module_path = (
        root_dir / root_package.replace(".", "/") / f"/{separator}/".join(list_modules)
    )


    parent_name: str = list_modules[0]  # родительское имя модуля
    full_name = None
    log_name = None
    package = None
    module_path = None
    created_paths: List = []
    for index, name in enumerate(list_modules, start=1):

        if name in reservied_names:
            raise RuntimeError(
                f"Имя модуля {name} уже используется системой и не может быть использовано"
            )

        if index == 1:  # если родительский модуль
            log_name: str = name
            full_name: str = name
            package: str = f"{root_package}.{name}"
            module_path: Path = root_dir / Path(package.replace(".", "/"))
        else:
            full_name = f"{full_name}.{separator}.{name}"
            package = f"{package}.{separator}.{name}"
            module_path = root_dir / Path(package.replace(".", "/"))

        if (
            module_path.exists()
        ):  # если модуль существует то проверяем его структуру и пропускаем итерацию
            if module_path == full_module_path:
                return fail(
                    code="Module is exists",
                    message=f"\nМодуль {module_path} уже существует",
                )

            result: Result = validate_module_structure(path=module_path)
            if not result.ok:
                return result
            continue
        module_path.mkdir(parents=True, exist_ok=True)
        for filename, content in template_files.items():
            created_paths.append(module_path)

            filepath: Path = module_path / filename
            temp_path: str = full_name.replace(".", "/")
            if not filepath.exists():
                try:  # проверяем корректность созданного контента
                    content: str = generate_content(
                        template=content,
                        log_name=log_name,
                        name_router_folders=name_router_folders,
                        name=full_name,
                        temp_path=temp_path,
                        root_package=package,
                        path_to_module=f"{temp_path}/{separator}",
                        root_childes=f"{package}.{separator}",
                        root_router_name=parent_name,
                        **requiered_field_modul.get_fields(),
                    )
                except KeyError as err:
                    save_delete_data(list_path=created_paths)
                    return fail(
                        code="Template Error",
                        message=f"Template error: {err}",
                    )

            filepath.write_text(data=content, encoding="utf-8")

        for dir_name in template_dirs:
            directory: Path = module_path / dir_name
            directory.mkdir(exist_ok=True)
            init_file: Path = directory / "__init__.py"
            if not init_file.exists():
                init_file.write_text("# init\n")

        # Проверка на валидность структуры модуля и файла настроек
        result_validate_structure = validate_module_structure(path=module_path)
        if not result_validate_structure.ok:
            save_delete_data(list_path=created_paths)  # удаляем созданые папки и файлы
            return result_validate_structure
        result_validate_settings_file = validate_module_settings_file(
            path=module_path, name=DEFAULT_NAME_SETTINGS
        )
        if not result_validate_settings_file.ok:
            save_delete_data(list_path=created_paths)  # удаляем созданые папки и файлы
            return result_validate_settings_file

    return ok(data="success")


def creates_new_modules_via_the_command_line(
    root_dir: Path,
    module_name: str,
    root_package: str,
    template_dirs: Dict = TEMPLATE_DIRS,
    template_files: Dict = TEMPLATE_FILES,
    separator: str = DEFAULT_CHILD_SEPARATOR,
) -> None:
    """
    Создает новые модули для бота через командную строку.

    Дочерний модуль должен быть разделен '.' от родительского модуля.
    Пример:

    cli add-module video.test.data

    """
    data: Result = create_module(
        module_name=module_name,
        root_package=root_package,
        root_dir=root_dir,
        template_files=template_files,
        template_dirs=template_dirs,
        separator=separator,
    )
    if not data.ok:
        print(data.error.message)
    else:
        print(f"Modules {module_name} created successfully")
