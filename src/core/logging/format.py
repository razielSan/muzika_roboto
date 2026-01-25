from dataclasses import dataclass


@dataclass
class LogFormat:
    """Содержит форматы для логгирования."""

    LOG_FORMAT: str = (
        "[%(asctime)s] - %(module)s:%(lineno)s - [%(levelname)s - %(message)s]"
    )
    DATE_FORMAT: str = "%Y-%m-%D %H-%M-%S"


log_format: LogFormat = LogFormat()
