from enum import Enum


class ErorrCode(Enum):
    UNKNOWN_ERROR: str = "UNKNOWN_ERROR"
    USER_ALREADY_EXISTS: str = "USER_ALREADY_EXISTS"


class NotFoundCode(Enum):
    USER_NOT_FOUND: str = "USER_NOT_FOUND"
    
    
class SuccessCode(Enum):
    SUCCESS_COLLECTION_SONG: str = "SUCCESS_COLLECTION_SONG"
