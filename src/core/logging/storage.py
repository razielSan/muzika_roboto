from typing import Dict

from core.response.response_data import LoggingData


class LoggerStorage:
    def __init__(self):
        self._loggers: Dict = {}

    def add(self, name: str, data: LoggingData):
        self._loggers[name] = data

    def get(self, name: str):
        return self._loggers[name]


storage: LoggerStorage = LoggerStorage()
