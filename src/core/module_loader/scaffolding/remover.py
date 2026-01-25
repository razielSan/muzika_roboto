import shutil
from pathlib import Path
import logging

from core.contracts.constants import DEFAULT_CHILD_SEPARATOR


def remove_module(
    name_module: str,
    log_path: Path,
    temp_path: Path,
    root_package: str,
    root_dir: Path,
    close_loggers: bool = True,
    tests: bool = False,
    separator: str = DEFAULT_CHILD_SEPARATOR,
):
    """
    Удаляет модуль и его дочерние модули, temp папку связанную с модулями и log модуля если родительский.А

    Args:
        name_module (str): Имя удаляемого модуля.Дочерние модули разделяются "."

        Пример:
        test.data

        log_path (Path): Путь до папки с логами
        temp_path (Path): Путь до папки temp
        root_package (str): Путь для модуля, от корневой директории до папки с модулями

        Пример:
        app.bot.moduels

        root_dir (Path): Путь до корневой директории

        close_loggers (bool, optional): Проверка на закрытие логов. По умолчанию True
        tests (bool, optional): Убирает вопрос что пользователь точно хочет удалить
        модуль. По умолчанию False

        separator: (str): Имя для связывыния дочернего и родительского модуля

        Имя папки для хранения дочерних модулей, формирования имен в settings,
        формирования имени роутера
    """

    # Закрываем логи, если есть открытые
    if close_loggers:
        logging.shutdown()

    path_name = name_module.replace(".", f"/{separator}/")

    root_package = Path(root_package.replace(".", "/"))
    modules_path: Path = root_dir / root_package / path_name
    if not modules_path.exists():
        print(f"Модуль {path_name} не найден")
        return

    result = None
    if not tests:
        result = input(
            f"Вы точно хотите удалить модуль - {path_name}\n1. "
            "Да - Нажмите 'Enter'\n2. Нет - Отправьте любой символ"
        )
    # 1. Удаляем модуль
    if not result:
        shutil.rmtree(modules_path)
        print(f"Модуль {path_name} " "и его дочерние модули успешно удалены")
    else:
        print(f"Удаление модуля {path_name} отменено")
        return

    # 2. Удаляем temp папки
    temp_folder: Path = temp_path / path_name
    if temp_folder.exists():
        shutil.rmtree(temp_folder)
        print(f"Удалена папка {temp_folder} и ее дочерние папки")

    # 3. Улаляем логи
    log_path: Path = log_path / path_name
    if log_path.exists():
        shutil.rmtree(log_path)
        print(f"Удалены логи - {log_path}")
