from typing import List, Dict

from core.response.messages import telegram_emoji


def get_info_executor(
    name: str,
    country: str,
    genres: List[str],
) -> str:
    genre_str: str = ", ".join(genres).strip()
    data: str = (
        f"{telegram_emoji.guitar} Исполнитель: "
        f"{name}\n{telegram_emoji.planet_earth}Страна: {country}\n\n"
        f"{telegram_emoji.piano_keys} Жанры: {genre_str}"
    )
    return data


def get_info_album(
    title: str,
    year: int,
):
    return (
        f"{telegram_emoji.guitar} Год: {year}\n"
        f"{telegram_emoji.guitar} Название: {title}"
    )


def get_info_photo(file_id: str, file_unique_id: str):
    return (
        f"Информация о фотографии:\n\nfile_id: {file_id}\n\n"
        f"file_unique_id: {file_unique_id}"
    )
