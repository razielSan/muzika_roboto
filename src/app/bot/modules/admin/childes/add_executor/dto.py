from typing import List

from pydantic import BaseModel, field_validator
from pathlib import Path
from app.bot.response import format_album


class ExecutorImportDTO(BaseModel):
    executor_name: str
    country: str
    genres: List[str]
    file_id: str
    file_unique_id: str
    base_path: Path

    @field_validator("executor_name")
    @classmethod
    def validator_executor_name(cls, value: str):
        if not (1 <= len(value) <= 200):
            raise ValueError(
                f"Название исполнителя должно быть от 1 до 200 символов: {value}"
            )
        return value.strip()

    @field_validator("country")
    @classmethod
    def validator_country(cls, value: str):
        if not (1 <= len(value) <= 100):
            raise ValueError(
                f"Название страны должно быть от 1 до 100 символов: {value}"
            )
        return value.strip()

    @field_validator("base_path")
    @classmethod
    def validator_base_path(cls, value: Path):
        if not value.exists():
            raise ValueError(f"Путь не существует: {value}")
        if not value.is_dir():
            raise ValueError(f"Путь должены быть директорией: {value}")
        for album_dir in value.iterdir():
            album_name = album_dir.stem
            result = album_name.strip(f"{format_album.YEAR_OPEN}").split(
                f"{format_album.YEAR_CLOSE}"
            )

            if len(result) != 2:
                raise ValueError(
                    f"Альбом должен содержать один знак {format_album.YEAR_CLOSE}: {album_name}"
                )
            year = result[0].isdigit()
            if not year:
                raise ValueError(
                    f"Год должен быть целым, положительным числом:  {result[0]}"
                )
        return value
