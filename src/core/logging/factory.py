from typing import Optional
from pathlib import Path
from logging import (
    Formatter,
    StreamHandler,
    FileHandler,
    getLogger,
    Logger,
    ERROR,
    INFO,
    WARNING,
    CRITICAL,
)
from sys import stdout
from pathlib import Path

from core.response.response_data import LoggingData


class LoggerFactory:
    def __init__(self, base_path: Path, format_log: str, datefmt: str):
        self.base_path = base_path
        self.format = format_log
        self.datefmt = datefmt

    def create(self, name: str, subdir: Optional[str] = None):
        base_path = self.base_path
        if subdir:
            base_path = self.base_path / subdir

        info_path: Path = base_path / "info.log"
        warning_path: Path = base_path / "warning.log"
        error_path: Path = base_path / "error.log"
        critical_path: Path = base_path / "critical.log"

        # Создаем папку "logs" если ее нет
        base_path.mkdir(parents=True, exist_ok=True)

        # задаем форматы логов
        formaterr: Formatter = Formatter(
            fmt=self.format,
            datefmt=self.datefmt,
        )

        # Потоковый обработчик для вывода в консоль
        stream_handler: StreamHandler = StreamHandler(stream=stdout)
        stream_handler.setFormatter(formaterr)

        # Файловые обработчики
        file_handler_info: FileHandler = FileHandler(
            filename=info_path,
            encoding="utf-8",
        )
        file_handler_info.setFormatter(formaterr)

        file_handler_warning: FileHandler = FileHandler(
            filename=warning_path, encoding="utf-8"
        )
        file_handler_warning.setFormatter(formaterr)

        file_handler_error: FileHandler = FileHandler(
            filename=error_path,
            encoding="utf-8",
        )
        file_handler_error.setFormatter(formaterr)

        file_handler_critical: FileHandler = FileHandler(
            filename=critical_path,
            encoding="utf-8",
        )
        file_handler_critical.setFormatter(formaterr)

        # Логгер для информации
        info_logger: Logger = getLogger(f"{name}_info")
        if not info_logger.handlers:
            info_logger.setLevel(level=INFO)
            info_logger.addHandler(file_handler_info)
            info_logger.addHandler(stream_handler)

        # Логгер для предупреждения
        warning_logger: Logger = getLogger(f"{name}_warning")
        if not warning_logger.handlers:
            warning_logger.setLevel(level=WARNING)
            warning_logger.addHandler(file_handler_warning)
            warning_logger.addHandler(stream_handler)

        # Логгер для ошибок
        error_logger: Logger = getLogger(f"{name}_error")
        if not error_logger.handlers:
            error_logger.setLevel(level=ERROR)
            error_logger.addHandler(file_handler_error)
            error_logger.addHandler(stream_handler)

        # Логгер для критических ошибок
        critical_logger: Logger = getLogger(f"{name}_critical")
        if not critical_logger.handlers:
            critical_logger.setLevel(level=CRITICAL)
            critical_logger.addHandler(file_handler_critical)
            critical_logger.addHandler(stream_handler)

        info_logger.info(f"Логгер {name} создан")
        return LoggingData(
            info_logger=info_logger,
            warning_logger=warning_logger,
            error_logger=error_logger,
            critical_logger=critical_logger,
            router_name=name,
        )
