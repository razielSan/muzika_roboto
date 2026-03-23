from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode


ERRORS = {
    ErorrCode.UNKNOWN_ERROR.name: "❌ Произошла неизвестная ошибка",
    ErorrCode.USER_ALREADY_EXISTS.name: "⚠ Пользователь уже существует",
    ErorrCode.EXECUTOR_ALREADY_EXISTS.name: "⚠ Исполнитель с таким именем и страной уже существует",
    ErorrCode.USER_EXECUTOR_ALREADY_EXISTS.name: "⚠ Исполнитель присутствует в библиотеке",
    ErorrCode.ALBUM_ALREADY_EXISTS.name: "⚠ Альбом уже существует",
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
    SuccessCode.GET_EXECUTORS_SUCCESS: "✅ Исполнители успешно получены",
    SuccessCode.GET_ALBUMS_SUCCESS.name: "✅ Альбомы успешно получены",
    SuccessCode.UPDATE_PHOTO_SUCCESS.name: "✅ Фото успешно изменено",
    SuccessCode.UPDATE_EXECUTOR_COUNTRY_SUCCESS.name: "✅ Страна успешно изменена",
    SuccessCode.UPDATE_GENRES_SUCCESS.name: "✅ Жанры успешно изменены",
    SuccessCode.UPDATE_NAME_SUCCESS.name: "✅ Имя успешно изменено",
    SuccessCode.UPDATE_SONG_TITLE_SUCCESS.name: "✅ Название "
    "песни успешно изменено\n\n✅ Новое название - {title}",
    SuccessCode.DELETE_SONGS_SUCCESS.name: "✅ Песни успешно удалены",
    SuccessCode.SYNC_EXECUTOR_SUCCESS.name: "✅ Исполнитель успешно добавлен в библиотеку",
    SuccessCode.DESYNC_EXECUTOR_SUCCESS.name: "✅ Исполнитель убран из библиотеки",
    SuccessCode.DELETE_EXECUTOR_SUCCESS.name: "✅ Исполнитель успешно удален из библиотеки",
    SuccessCode.DELETE_ALBUM_SUCCES.name: "✅ Альбом успешно удален из библиотеки",
}

LIMIT_COLLECTION_SONGS: int = 3
LIMIT_ALBUMS: int = 5
LIMIT_SONGS: int = 5


def resolve_message(code: str):
    if code in ERRORS:
        return ERRORS[code]
    if code in NOT_FOUND:
        return NOT_FOUND[code]
    if code in SUCCESS:
        return SUCCESS[code]
    return "Unknown"


class UserMessages:
    CONFIRMATION_TEXT: str = "✅ Подтверждаю"
    CAPTION_DELETE_EXECUTOR: str = "❗️ Вы действительно хотите удалить исполнителя ?"
    CAPTION_DELETE_ALBUM: str = "❗️ Вы действительно хотите удалить альбом ?"
    CLICK_ONE_OF_THE_BUTTONS_ABOVE: str = "👆🏾 Нажмите одну из кнопок выше"
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
    THERE_ARE_NO_SONGS: str = "🤷🏻‍♀️ У вас нет песен в сборнике"
    THE_SONG_HAS_ALREADY_BEEN_ADDED: str = "🤷🏻‍♀️ Песня {title} уже была добавленна"
    THE_SONG_IS_SAVED: str = "🎼 Песня {title} была сохранена"
    THE_DATA_MUST_BE_IN_THE_FORMAT: str = "🖊 Данные должны быть в формате\n\n{format}"
    USER_CANCEL_MESSAGE: str = "❌ Все запросы отменены"
    USER_PANEL_CAPTION: str = "🤔 Что же мне сегодня послушать ?"


user_messages: UserMessages = UserMessages()
