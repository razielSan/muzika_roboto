from urllib.parse import urlparse

from core.response.response_data import Result
from core.error_handlers.helpers import ok, fail


def checking_base64(data: str) -> bool:
    """
    Проверяет, являются ли входящие данные в формате base64.

    Args:
        data (str): Данные для проверки

    Returns:
        bool: True or False
    """
    if data.startswith("http"):
        return False
    return True


def check_number_is_positivity(number: str) -> Result:
    """
    Проверяет, является ли входящее  значение положительным числом.

    Args:
        number (str): Данные для проверки

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
        number: int = int(number)
        if number <= 0:
            return fail(
                code="FAILED CHECK POSITIVITY", message="⚠ Число должно быть больше 0"
            )
        return ok(data=number)
    except Exception:
        return fail(
            code="FAILED CHECK POSITIVITY", message="⚠ Данные должны быть целым числом"
        )


def is_valid_url(url: str) -> bool:
    """Проверяет url на валидность."""
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme and parsed.netloc)
    except Exception:
        return False
