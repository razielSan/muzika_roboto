from dataclasses import dataclass
from enum import Enum


class KeyboardResponse(Enum):
    YES: str = "✅ [ Да ]"
    NO: str = "❌ [ Нет ]"
    ADD_SONGS: str = "🎼 Добавить Песни"
    ADD_ALBUM: str = "🎼 Добавить Альбом"
    CANCEL_THE_DELETION_OF_SONGS: str = "❌ ОТМЕНИТЬ УДАЛЕНИЕ"
    CONFIRM_THE_DELETION_OF_SONGS: str = "✅ НАЖМИТЕ ДЛЯ ПОДТВЕРЖДЕНИЯ"
    CREATE_EXECUTOR: str = "👩🏾‍💻 Создание исполнителя"
    CREATE_EXECUTOR_WITH_ALBUMS: str = "👩🏾‍💻 Создание исполнителя с альбомами"
    BACK_TO_THE_ADMIN_PANEL: str = "⬅ Назад к админ панели"
    BACK_TO_THE_USER_PANEL: str = "⬅ Назад к главной панели"
    BACK_TO_ALBUMS: str = "⬅ Назад к альбомам"
    BACK_BUTTON: str = "⬅ Назад"
    DELETE_SONGS: str = "🗑 Удалить Песни"
    DELETE_ALBUM: str = "🗑 Удалить Альбом"
    DELETE_EXECUTOR: str = "🗑 Удалить Исполнителя"
    FORWARD_BUTTON: str = "Вперед ➡"
    NOT_FOUND_EXECUTORS: str = "🤷🏻‍♀️ Нет загруженных исполнителей"
    NOT_FOUND_ALBUMS: str = "🤷🏻‍♀️ Нет загруженных альбомов"
    NOT_FOUND_SONGS: str = "🤷🏻‍♀️ Нет загруженных песен"
    UPDATE_PHOTO_EXECUTOR: str = "📆 Обновить Фото Исполнителя"
    UPDATE_PHOTO_ALBUM: str = "📆 Обновить Фото Альбома"
    UPDATE_PHOTO_COLLECTION_SONGS: str = "📆 Обновить Фото Сборника Песен"
    UPDATE_NAME_EXECUTOR: str = "📆 Обновить Имя Исполнителя"
    UPDATE_TITLE_ALBUM: str = "📆 Обновить Заголовок Альбома"
    UPDATE_YEAR_ALBUM: str = "📆 Обновить Год Альбома"
    UPDATE_TITLE_SONG: str = "📆 Обновить Имя Песни"
    UPDATE_EXECUTOR_GENRES: str = "📆 Обновить Жанры Исполнителя"
    UPDATE_COUNTRY_EXECUTOR: str = "📆 Обновить Страну Исполнителя"
    SYNC_EXECUTOR: str = "👯‍♂️ Довавить В Библиотеку"
    DESYNC_EXECUTOR: str = "🗑 Убрать Из Библиотеки"



@dataclass
class FomatAlbum:
    FORMAT_ALBUM: str = "(<year>) <name_album>"
    YEAR_OPEN: str = "("
    YEAR_CLOSE: str = ")"


format_album = FomatAlbum()
