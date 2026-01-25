from core.logging.storage import LoggerStorage
from core.response.response_data import LoggingData


class LoggerRuntime:
    _storage = None

    @classmethod
    def init(cls, storage: LoggerStorage):
        if cls._storage is not None:
            raise RuntimeError("Logging already initialized")
        cls._storage = storage

    @classmethod
    def get(cls, name: str) -> LoggingData:
        if cls._storage is None:
            raise RuntimeError("Logging not initialized")
        return cls._storage.get(name)
