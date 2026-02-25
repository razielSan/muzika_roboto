from dataclasses import dataclass
from enum import Enum


LIMIT_SONGS: int = 5
LIMIT_ALBUMS: int = 5


class KeyboardResponse(Enum):
    YES: str = "[ Да ]"
    NO: str = "[ Нет ]"
    CANCEL_THE_DELETION_OF_SONGS: str = "ОТМЕНИТЬ УДАЛЕНИЕ ПЕСЕН"
    CONFIRM_THE_DELETION_OF_SONGS: str = "ПОДТВЕРДИТЬ УДАЛЕНИЕ ПЕСЕН"
    BACK_TO_THE_ADMIN_PANEL: str = "⬅ Назад к админ панели"
    BACK_TO_ALBUMS: str = "⬅ Назад к альбомам"
    UPDATE_PHOTO_EXECUTOR: str = "📆 Обновить Фото Исполнителя"
    UPDATE_PHOTO_ALBUM: str = "📆 Обновить Фото Альбома"
    UPDATE_NAME_EXECUTOR: str = "📆 Обновить Имя Исполнителя"
    UPDATE_TITLE_ALBUM: str = "📆 Обновить Заголовок Альбома"
    UPDATE_YEAR_ALBUM: str = "📆 Обновить Год Альбома"
    UPDATE_TITLE_SONG: str = "📆 Обновить Имя Песни"
    UPDATE_EXECUTOR_GENRES: str = "📆 Обновить Жанры Исполнителя"
    UPDATE_COUNTRY_EXECUTOR: str = "📆 Обновить Страну Исполнителя"
    ADD_SONGS: str = "🎼 Добавить Песни"
    ADD_ALBUM: str = "🎼 Добавить Альбом"
    DELETE_SONGS: str = "🗑 Удалить Песни"
    DELETE_ALBUM: str = "🗑 Удалить Альбом"
    DELETE_EXECUTOR: str = "🗑 Удалить Исполнителя"
    BACK_BUTTON: str = "⬅ Назад"
    FORWARD_BUTTON: str = "Вперед ➡"


@dataclass
class FomatAlbum:
    FORMAT_ALBUM: str = "(<year>) <name_album>"
    YEAR_OPEN: str = "("
    YEAR_CLOSE: str = ")"


format_album = FomatAlbum()
