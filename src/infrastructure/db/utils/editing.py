from typing import List


def get_information_executor(
    name: str,
    country: str,
    genres: List[str],
    len_albums: int,
) -> str:
    genre_str: str = ", ".join(genres).strip()
    data: str = (
        "🎸 Исполнитель: "
        f"{name}\n🌏 Страна: {country}\n\n"
        f"🎹 Жанры: {genre_str}\n"
        f"🎺 Количество альбомов: {len_albums}"
    )

    return data
