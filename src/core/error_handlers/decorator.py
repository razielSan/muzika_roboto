from typing import Optional, Callable
import functools
from asyncio import exceptions

from core.error_handlers.format import format_errors_message
from core.response.response_data import LoggingData
from core.error_handlers.helpers import fail, ok
from core.response.messages import messages


def safe_async_execution(logging_data: LoggingData = None):
    """
    Декоратор оборчивающий асинхронную функцию в try/except для перхвата всех возможных ошибок.

    При ошибке в ходе выполнения функции выкидывает обьект класса Result

    Args:
       logging_data (LoggingData, optional): Обьект класса LoggingData.По умолчанию None

        аргументы LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)
    """

    def decorator(function: Callable):
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            try:
                return await function(*args, **kwargs)

            except exceptions.CancelledError:
                print("Остановка работы процесса пользователем")
                return ok(data="Остановка работы процесса пользователем")

            except Exception as err:
                if logging_data:
                    logging_data.error_logger.exception(
                        format_errors_message(
                            name_router=logging_data.router_name,
                            method="<unknown>",
                            status=0,
                            url="<unknown>",
                            error_text=err,
                            function_name=function.__name__,
                        )
                    )
                else:
                    print(err)
                return fail(code="Unknown error", message=messages.SERVER_ERROR)

        return wrapper

    return decorator


def safe_sync_execution(logging_data: LoggingData = None):
    """
        Декоратор оборчивающий синхронную функцию в try/except для перхвата всех возможных ошибок.
        При ошибке в ходе выполнения функции выкидвает обьект класса Result

    Args:
        logging_data (LoggingData, optional): Обьект класса LoggingData.По умолчанию None

        атрибуты LoggingData:
            - info_logger (Logger)
            - warning_logger (Logger)
            - error_logger (Logger)
            - critical_logger (Logger)
            - router_name (str)
    """

    def decorator(function: Callable):
        @functools.wraps(function)
        def wrapper(*args, **kwargs):
            try:
                return function(*args, **kwargs)
            except Exception as err:
                if logging_data:
                    logging_data.error_logger.exception(
                        format_errors_message(
                            name_router=logging_data.router_name,
                            method="<unknown>",
                            status=0,
                            url="<unknown>",
                            error_text=err,
                            function_name=function.__name__,
                        )
                    )
                else:
                    print(err)
                return fail(code="Unknown error", message=messages.SERVER_ERROR)

        return wrapper

    return decorator
