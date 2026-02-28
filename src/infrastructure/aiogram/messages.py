from domain.errors.error_code import ErorrCode, NotFoundCode


ERRORS = {
    ErorrCode.UNKNOWN_ERROR.name: "❌ Произошла неизвестная ошибка",
    ErorrCode.USER_ALREADY_EXISTS.name: "⚠ Пользователь уже существует",
}


NOT_FOUND = {
    NotFoundCode.USER_NOT_FOUND.name: "⚠ Пользователь не найден\n\n"
    "🤷🏻‍♀️ Попробуйте нажать /start"
}
SUCCESS = {}

LIMIT_COLLECTION_SONGS = 10


def resolve_error_message(error_code: str):
    if error_code in ERRORS:
        return ERRORS[error_code]
    if error_code in NOT_FOUND:
        return NOT_FOUND[error_code]
    return "❌ Unknown"


class UserMessages:
    USER_CANCEL_MESSAGE: str = "❌ Все запросы отменены"
    CONFIRMATION_TEXT: str = "✅ Подтверждаю"
    USER_CANCEL_TEXT: str = "🚫 Отмена"
    DROP_THE_SONG: str = "🎸 Скидывайте песни"
    ENTER_THE_SONG_NAME: str = "🖌 Введите имя песни"
    ENTER_THE_SONG_POSITION: str = "🖌 Введите позицию песни"
    THERE_ARE_NO_SONGS: str = "🤷🏻‍♀️ У вас нет песен добавленных песен"
    THE_SONG_HAS_ALREADY_BEEN_ADDED: str = "🤷🏻‍♀️ Песня {title} уже была добавленна"
    THE_SONG_IS_SAVED: str = "🎼 Песня {title} была сохранена"
    MAIN_MENU: str = "📻 Главное меню"
    NO_SONGS_WERE_DROPPED: str = "🤷🏻‍♀️ Не было сброшено песен"
    SONGS_WILL_BE_ADDED_IN_QUANTITY: str = (
        "✅ Будут добавлены песни\n\n✅ Количество {count}"
    )
    THE_DATA_MUST_BE_IN_THE_FORMAT: str = "🖊 Данные должны быть в формате {format}"
    MY_COLLECTION_OF_SONGS: str = "🎧 Мой сборник песен"
    SONGS_ADDED_SUCCESSSFULLY: str = "✅ Песни успешно добавлены"
    PRESS_ONE_OF_THE_BUTTONS: str = "👇 Нажмите одну из кнопок"
    THE_NAME_OF_THE_SONG_HAS_BEEN_SUCCESSFULLY_CHANGED: str = (
        "✅ Название " "песни успешно изменено\n\n✅ Новое название - {title}"
    )
    NO_SONGS_FOUND_WITH_THE_POSITION: str = "⚠️ Не найдено песни с позицией {position}"


user_messages: UserMessages = UserMessages()
