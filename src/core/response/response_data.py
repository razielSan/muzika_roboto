from typing import Optional, Any, Dict
from dataclasses import dataclass
from logging import Logger

from pydantic import BaseModel


class Error(BaseModel):
    """Модель для ошибок"""

    code: str
    message: str
    details: Optional[Any] = None


class Result(BaseModel):
    """Модель для ответа."""

    ok: bool
    data: Optional[Any] = None
    error: Optional[Error] = None


class NetworkResponseResult(BaseModel):
    """Модель для сетевого ответа."""

    ok: bool
    data: Optional[Any] = None
    url: str
    status: int
    method: str
    headers: Optional[Dict] = None
    error: Optional[Error] = None


@dataclass
class LoggingData:
    """Модель для возврата логгеров."""

    info_logger: Logger
    warning_logger: Logger
    error_logger: Logger
    critical_logger: Logger
    router_name: str


@dataclass
class InlineKeyboardData:
    """Модель для инлайн клавиатуры."""

    text: str
    callback_data: str
    resize_keyboard: bool = True
