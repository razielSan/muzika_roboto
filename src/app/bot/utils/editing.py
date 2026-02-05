from typing import List

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
