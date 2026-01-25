from core.response.response_data import LoggingData
from core.logging.runtime import LoggerRuntime


def get_loggers(name: str) -> LoggingData:
    """
    Возвращает склад ля логов конкретного роутера.

    Args:
        name (str): имя роутера

    Returns:
        LoggingData: хранилище для логов
    """
    logging_data = LoggerRuntime.get(name=name)

    return logging_data
