from typing import List


def get_information_executor(
    name: str,
    country: str,
    genres: List[str],
    number_of_albums: int,
) -> str:
    genre_str: str = ", ".join(genres).strip()
    data: str = (
        "🎸 Исполнитель: "
        f"{name}\n🌏 Страна: {country}\n\n"
        f"🎹 Жанры: {genre_str}\n"
        f"🎺 Количество альбомов: {number_of_albums}"
    )

    return data


def get_information_album(
    title: str,
    year: int,
    number_of_songs: int
):
    return (
        f"🎸 Год: {year}\n"
        f"🎸 Название: {title}\n"
        f"🎸 Количестов песен: {number_of_songs}"
    )
