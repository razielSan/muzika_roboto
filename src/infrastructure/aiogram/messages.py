from typing import Dict

from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from infrastructure.aiogram.response import format_album

ERRORS = {
    ErorrCode.UNKNOWN_ERROR.name: "❌ Произошла неизвестная ошибка",
    ErorrCode.INVALID_TELEGRAM.name: "⚠ Telegam должен быть числом",
    ErorrCode.USER_ALREADY_EXISTS.name: "⚠ Пользователь уже существует",
    ErorrCode.EXECUTOR_ALREADY_EXISTS.name: "⚠ Исполнитель с таким именем и страной уже существует",
    ErorrCode.USER_EXECUTOR_ALREADY_EXISTS.name: "⚠ Исполнитель присутствует в библиотеке",
    ErorrCode.ALBUM_ALREADY_EXISTS.name: "⚠ Альбом уже существует",
    ErorrCode.GENRE_DOES_NOT_EXIST.name: "⚠ Жанр не существует",
    ErorrCode.CANCEL_ERROR.name: "❌ Отменены все действия",
    ErorrCode.INVALID_USER_NAME.name: "⚠ Имя пользователя должно быть строкой",
    ErorrCode.INVALID_USER_ID.name: "⚠ USER ID должен быть числом или None",
    ErorrCode.INVALID_EXECUTOR_NAME.name: "⚠ Имя исполнителя должно быть строкой",
    ErorrCode.INVALID_EXECUTOR_GENRES.name: "⚠ Жанры должны быть списком из строк",
    ErorrCode.INVALID_EXECUTOR_COUNTRY.name: "⚠ Страна должна быть строкой",
    ErorrCode.INVALID_EXECUTOR_ID.name: "⚠ EXECUTOR ID должен быть числом ",
    ErorrCode.INVALID_ALBUM_ID.name: "⚠ ALBUM ID должнен быть числом",
    ErorrCode.INVALID_LEN_DATA.name: "⚠ Данные должны быть больше 0 и не быть пустым значением",
    ErorrCode.FAILED_CHECK_POSITIVITY.name: "⚠ {data} должен быть числом и больше 0"
}


NOT_FOUND = {
    NotFoundCode.USER_NOT_FOUND.name: "⚠ Пользователь не найден\n\n"
    "🤷🏻‍♀️ Нажмите /start для регистрации",
    NotFoundCode.SONGS_NOT_FOUND.name: "⚠ Песни не найдены",
    NotFoundCode.SONG_NOT_FOUND.name: "⚠ Песня не найдена",
    NotFoundCode.SONG_POSITION_NOT_FOUND.name: "⚠ Песня c позицией {position} не найдена",
    NotFoundCode.EXECUTORS_NOT_FOUND.name: "⚠ Не найден ни один исполнитель",
    NotFoundCode.EXECUTOR_NOT_FOUND.name: "⚠ Исполнитель не найден",
    NotFoundCode.ALBUM_NOT_FOUND.name: "⚠ Альбом не найден",
    NotFoundCode.USER_EXECUTOR_NOT_FOND.name: "⚠ В библиотеке не исполнителей",
}
SUCCESS = {
    SuccessCode.ADD_EXECUTOR_SUCCESS.name: "✅ Исполнитель успешно создан",
    SuccessCode.ADD_SONGS_SUCCESS.name: "✅ Песни успешно добавлены",
    SuccessCode.ADD_USER_SUCCESS.name: "✅ Пользователь успешно добавлен",
    SuccessCode.ADD_AlBUM_SUCCESS.name: "✅ Альбом успешно добавлен",
    SuccessCode.GET_SONGS_SUCCESS.name: "✅ Песни успешно получены",
    SuccessCode.GET_EXECUTORS_SUCCESS.name: "✅ Исполнители успешно получены",
    SuccessCode.GET_ALBUMS_SUCCESS.name: "✅ Альбомы успешно получены",
    SuccessCode.UPDATE_PHOTO_SUCCESS.name: "✅ Фото успешно изменено",
    SuccessCode.UPDATE_EXECUTOR_COUNTRY_SUCCESS.name: "✅ Страна исполнителя успешно изменена",
    SuccessCode.UPDATE_GENRES_SUCCESS.name: "✅ Жанры успешно изменены",
    SuccessCode.UPDATE_NAME_SUCCESS.name: "✅ Имя успешно изменено",
    SuccessCode.UPDATE_ALBUM_YEAR_SUCCESS.name: "✅ Год выхода альбома успешно изменен",
    SuccessCode.UPDATE_ALBUM_TITLE_SUCCESS.name: "✅ Заголовок альбома успешно изменен",
    SuccessCode.UPDATE_SONG_TITLE_SUCCESS.name: "✅ Название "
    "песни успешно изменено\n\n✅ Новое название - {title}",
    SuccessCode.DELETE_SONGS_SUCCESS.name: "✅ Песни успешно удалены",
    SuccessCode.SYNC_EXECUTOR_SUCCESS.name: "✅ Исполнитель успешно добавлен в библиотеку",
    SuccessCode.DESYNC_EXECUTOR_SUCCESS.name: "✅ Исполнитель убран из библиотеки",
    SuccessCode.DELETE_EXECUTOR_SUCCESS.name: "✅ Исполнитель успешно удален из библиотеки",
    SuccessCode.DELETE_ALBUM_SUCCES.name: "✅ Альбом успешно удален из библиотеки",
    SuccessCode.VALIDATE_USER_SUCCES.name: "✅ Валидация данных пользователя прошла успешно",
}

LIMIT_COLLECTION_SONGS: int = 5
LIMIT_ALBUMS: int = 5
LIMIT_SONGS: int = 5
LIMIT_SEARCH_EXECUTOR: int = 5

GENRES: Dict = {
    1: "punk-rock",
    2: "hardcore",
    3: "alternative metal",
    4: "8-bit",
    5: "grindcore",
    6: "electronic music",
    7: "crust",
    8: "game covers",
    9: "anarcho-punk",
    10: "metal",
    11: "d-beat",
    12: "stenchcore",
    13: "rap",
    14: "russian rock",
    15: "classic music",
    16: "anarcho-chanson",
}


def resolve_message(code: str):
    if code in ERRORS:
        return ERRORS[code]
    if code in NOT_FOUND:
        return NOT_FOUND[code]
    if code in SUCCESS:
        return SUCCESS[code]
    return "Unknown"


class UserMessages:
    ADD_SONGS_MESSAGE: str = "✅ ({year}) {title}\n⌛️ {song} - идет добавление песни"
    ADD_SONGS_COMPLETE: str = "✅ ({year}) {title}\n✅ {song} - песня добавлена"
    BACK_ALBUM_PAGE: str = "✅ Возвращение на страницу альбома"
    BACK_EXECUTOR_PAGE: str = "✅ Возвращение на страницу исполнителя"
    CONFIRMATION_TEXT: str = "✅ Подтверждаю"
    CAPTION_DELETE_EXECUTOR: str = "❗️ Вы действительно хотите удалить исполнителя ?"
    CAPTION_DELETE_ALBUM: str = "❗️ Вы действительно хотите удалить альбом ?"
    CLICK_ONE_OF_THE_BUTTONS_ABOVE: str = "👆🏾 Нажмите одну из кнопок выше"
    CLICK_CANCEL_BUTTON: str = "{button}: Отменить все действия"
    CLICK_UNKNOWN_BUTTON: str = "Неизвестно: Название по умолчанию"
    DROP_THE_SONG: str = "❗️ Скидывайте песни"
    DROP_THE_PHOTO: str = "❗️ Скидывайте фотографию"
    ENTER_THE_SONG_NAME: str = "❗️ Введите имя песни"
    ENTER_THE_ALBUM_TITLE: str = "❗️ Введите заголовок альбома"
    ENTER_THE_ALBUM_YEAR: str = "❗️ Введите год выхода альбома"
    ENTER_THE_СOUNTRY_EXECUTOR: str = "❗️ Введите страну исполнителя"
    ENTER_THE_PHOTO_DEFAULT: str = (
        "❗️ Скидывайте фотографию\n\n🖌 Любой символ: Дефолтная фотография"
    )
    ENTER_THE_GENRES: str = (
        "❗️ Введите жанры исполнителя через точку\n\n"
        "🖌 Пример: панк-рок.метал.русский рок\n\n"
    )
    ENTER_THE_EXECUTOR_NAME: str = "❗️ Введите имя исполнителя"
    ENTER_THE_FULL_ALBUM_PATH: str = (
        "❗️ Введите путь до альбомов исполнителя"
        f"\n\n{format_album.FORMAT_ALBUM}: формат альбома"
    )
    ENTER_THE_SONG_POSITION: str = "❗️ Введите позицию песни"
    MESSAGE_TO_CONFIRM_THE_DELETION_OF_SONGS: str = (
        "❗️ Подтвердите"
        " песни для удаления\n\n✅ Количество: {count}\n✅ Позиции песен: {positions}"
    )
    MAIN_MENU: str = "🎤 Главное меню"
    MY_MUSIC_COLLECTION: str = "📻 Моя Музыкальная Коллекция"
    MY_COLLECTION_OF_SONGS: str = "🎧 Мой сборник песен"
    NO_SONGS_WERE_DROPPED: str = "🤷🏻‍♀️ Не было сброшено песен"
    PRESS_ONE_OF_THE_BUTTONS: str = "👇 Нажмите одну из кнопок"
    PRESSING_THE_BUTTON_AGAIN_EXECUTOR: str = "❗️ Исполнитель уже загружен"
    SONGS_WILL_BE_ADDED_IN_QUANTITY: str = (
        "✅ Будут добавлены песни\n\n✅ Количество {count}"
    )
    SELECT_THE_SONGS_TO_DELETE: str = "❗️ Выберите песни для удаления"
    SEARCH_RESULT: str = "✅ Результаты поиска"
    WAIT_MESSAGE: str = "⌛️ Идет процесс обработки данных...."
    THERE_ARE_NO_SONGS: str = "🤷🏻‍♀️ У вас нет песен в сборнике"
    THE_SONG_HAS_ALREADY_BEEN_ADDED: str = "🤷🏻‍♀️ Песня {title} уже была добавленна"
    THE_SONG_IS_SAVED: str = "🎼 Песня {title} была сохранена"
    THE_DATA_MUST_BE_IN_THE_FORMAT: str = (
        "⚠ Данные должны" " быть в формате\n\n{format}\n\n🖌 Отправляйте, снова, данные"
    )
    USER_CANCEL_MESSAGE: str = "❌ Все запросы отменены"
    USER_PANEL_CAPTION: str = "🤔 Что же мне сегодня послушать ?"
    ADMIN_PANEL_CAPTION: str = "🔧 Админ Панель"


user_messages: UserMessages = UserMessages()
