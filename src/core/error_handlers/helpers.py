from typing import Callable, Optional, Union, Any, Dict
from asyncio import AbstractEventLoop, exceptions
import functools
import traceback
import importlib

from core.response.response_data import (
    LoggingData,
    Result,
    Error,
    NetworkResponseResult,
)
from core.error_handlers.format import format_errors_message
from core.response.messages import messages


def ok(data: None, empty: bool = False) -> Result:
    """Возвращает класс Result для успешного запроса."""

    return Result(
        ok=True,
        data=data,
        empty=empty,
    )


def fail(
    code: str,
    message: str,
    details: Any = None,
) -> Result:
    """Возвращает класс Result для неуспешного запроса."""
    return Result(
        ok=False,
        error=Error(
            code=code,
            message=message,
            details=details,
        ),
    )


def network_ok(
    data: Any,
    url: str,
    status: int,
    method: str,
    headers: Dict = None,
) -> NetworkResponseResult:
    """Возвращает класс NetworkResponseResult для успешного запроса."""
    return NetworkResponseResult(
        ok=True,
        data=data,
        url=url,
        status=status,
        method=method,
        headers=headers,
    )


def network_fail(
    code: str,
    message: str,
    url: str,
    status: int,
    method: str,
    details: Any = None,
    headers: Dict = None,
) -> NetworkResponseResult:
    """Возвращает класс NetworkResponseResult для неуспешного запроса."""
    return NetworkResponseResult(
        ok=False,
        url=url,
        status=status,
        method=method,
        headers=headers,
        error=Error(
            code=code,
            message=message,
            details=details,
        ),
    )


async def run_safe_inf_executror(
    loop: AbstractEventLoop,
    func: Callable,
    *args,
    logging_data: LoggingData = None,
    **kwargs,
) -> Union[Any, Result]:
    """
    Отлавливает все возможные ошибки для переданной синхронной функции.

    При ошибке в ходе выполнения функции выкидывает обьект класса ResponseData

    Args:
        loop (AbstractEventLoop): цикл событий
        func (Callable): функция для цикла
        logging_data (LoggingData, optional): Обьект класса LoggingData.По умолчанию None

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)

    Returns:
        Union[Any, Result]: Возвращает результат функции func
    """
    try:
        return await loop.run_in_executor(
            None,
            functools.partial(
                func,
                *args,
                **kwargs,
            ),
        )
    except exceptions.CancelledError:
        print("Остановка работы процесса пользователем")

    except Exception as err:
        if logging_data:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    status=0,
                    method="<unknown>",
                    url="<unknown>",
                    error_text=err,
                    function_name=func.__name__,
                )
            )
        else:
            print(err)

        return fail(code="Unknown error", message=messages.SERVER_ERROR)


def safe_import(
    module_package: str,
    logging_data: LoggingData = None,
) -> Result:
    """
    Безопасный импорт модуля.

    Args:
        module_package (str): Путь для импорта

        Пример:
        app.bot.modules.test.settings

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
        return ok(data=importlib.import_module(module_package))
    except Exception as err:
        if logging_data:
            logging_data.error_logger.error(
                format_errors_message(
                    name_router=logging_data.router_name,
                    error_text=f"[IMPORT ERROR] Модуль {module_package} не загрузился\n"
                    f"{err}\n{traceback.format_exc()}",
                    function_name=safe_import.__name__,
                )
            )
        else:
            print(
                f"[IMPORT ERROR] Модуль {module_package} не загрузился\n{traceback.format_exc()}"
            )

        return fail(
            code="IMPORT ERROR",
            message=f"Модуль {module_package} не загрузился\n{err}",
        )
