from typing import Tuple, List
from pathlib import Path
import shutil
import os
import time
import traceback

from core.response.response_data import LoggingData
from core.error_handlers.format import format_errors_message
from core.response.messages import telegram_emoji
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


def ensure_directories(
    *args: Path,
    logging_data: LoggingData = None,
) -> Result:
    """
    Проверяет наличие переданных путей и создает их при необходимости.

    Args:
        logging_data (LoggingData, optional): Обьект класса LoggingData.По умолчанию None

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)

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
    try:
        directory = None
        requiered_dirs: Tuple[Path, ...] = args

        for directory in requiered_dirs:
            directory.mkdir(parents=True, exist_ok=True)
            if logging_data:
                logging_data.info_logger.info(f"Директория {directory} создана")
        return ok(data="success")
    except Exception as err:
        logging_data.error_logger.error(
            msg=format_errors_message(
                name_router=logging_data.router_name,
                error_text=f"Ошибка при создании директории"
                f" - {directory}\n{traceback.format_exc()}",
                function_name=ensure_directories.__name__,
            )
        )
        return fail(
            code="DIRECTORY CREATE ERROR",
            message=f"Ошибка при создании директории - {directory}\n{err}",
            details=str(traceback.format_exc()),
        )


def delete_all_files_and_symbolik_link(
    path_folder: Path,
    logging_data: LoggingData,
) -> None:
    """
    Удаляет все файлы в папке.

    Args:
        path_folder (Path): Путь до папки
        logging_data (LoggingData): Обьект класса LoggingData

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)

    """
    # Проверяем есть ли папка в наличии
    if not path_folder.exists():
        return

    for filename in os.listdir(path_folder):
        try:
            filepath: str = os.path.join(path_folder, filename)
            if os.path.isfile(filepath) or os.path.islink(filepath):
                os.remove(filepath)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    method="<unknown>",
                    status=0,
                    url="<unknown>",
                    error_text=str(err),
                    function_name=delete_all_files_and_symbolik_link.__name__,
                )
            )


def save_delete_data(
    list_path: List[Path],
    logging_data: LoggingData = None,
    retries: int = 3,
) -> None:
    """Удаляет данные по переданному пути.

    Args:
        list_path (List[Path]): Список с путями до данных
        logging_data (LoggingData, optional): логгер для записи в лог. По умолчанию None

        logging_data (LoggingData): Обьект класса LoggingData

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)

        retries (int): Количество попыток для удаления данных
    """
    for path in list_path:
        for _ in range(retries):
            try:
                if path.is_file():
                    path.unlink()
                if path.is_dir():
                    shutil.rmtree(path=path)

            except PermissionError:
                time.sleep(1)
            except Exception as err:
                message: str = f"Ошибка при удалении {path}: {err}"
                if logging_data:
                    logging_data.warning_logger.warning(msg=message)
                else:
                    print(f"Failed to cleanup: {path}")


def make_archive(
    base_name: str,
    format_archive: str,
    root_dir: Path,
    base_dir: str,
    logging_data: LoggingData,
) -> Result:
    """
    Создает архив по переданному пути.

    Args:
        base_name (str): Путь сохранения архива.Содержит в себе имя архива без расширения

        Пример
        app/bot/temp/video/video

        format_archive (str): Формат архива
        root_dir (Path): Путь к файлам которые нужно архивировать
        base_dir (str): Каталог, откуда начинается архивирование

        Пример
        "." - архивирует все файлы в сам архив без создания папок

        logging_data (LoggingData): Обьект класса LoggingData

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)


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
    try:
        shutil.make_archive(
            base_name=base_name,
            format=format_archive,
            root_dir=root_dir,
            base_dir=base_dir,
        )
        return ok(data=base_name)
    except Exception as err:
        logging_data.error_logger.exception(
            format_errors_message(
                name_router=logging_data.router_name,
                method="<unknown>",
                status=0,
                url="<unknown>",
                error_text=str(err),
                function_name=make_archive.__name__,
            )
        )
        return fail(
            code="ARCHIVE CREATE ERROR",
            message=f"{telegram_emoji.red_cross} Ошибка при создании архива",
        )
