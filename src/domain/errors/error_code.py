from enum import Enum


class ErorrCode(Enum):
    UNKNOWN_ERROR: str = "UNKNOWN_ERROR"


class ExistsErrorCode(Enum):
    USER_ALREADY_EXISTS: str = "USER_ALREADY_EXISTS"
