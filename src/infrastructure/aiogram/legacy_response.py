from enum import Enum


class ServerDatabaseResponse(Enum):

    # коды удачных запросов
    SUCCESS_UPDATE_PHOTO_EXECUTOR: str = "✅ Фото исполнителя успешно изменено"
    SUCCESS_UPDATE_EXECUTOR_NAME: str = "✅ Имя исполнителя успешно изменено"
    SUCCESS_UPDATE_EXECUTOR_COUNTRY: str = "✅ Страна исполнителя успешно изменена"
    SUCCESS_UPDATE_EXECUTOR_GENRES: str = "✅ Жанры исполнителя успешно изменены"
    SUCCESS_UPDATE_PHOTO_ALBUM: str = "✅ Фото альбома успешно изменено"
    SUCCESS_UPDATE_ALBUM_TITLE: str = "✅ Имя альбома успешно изменено"
    SUCCESS_UPDATE_ALBUM_YEAR: str = "✅ Год выпуска альбома успешно изменен"
    SUCCESS_UPDATE_TITLE_SONG: str = "✅ Имя песни успешно обновлено"
    SUCCESS_DELETE_EXECUTOR: str = "✅ Исполнитель успешно удален"
    SUCCESS_DELETE_ALBUM: str = "✅ Альбом успешно удален"
    SUCCESS_DELETE_SONGS: str = "✅ Песни успешно удалены"
    SUCCESS_ADD_EXECUTOR: str = "✅ {name}: {country} с альбомами был создан"
    SUCCESS_ADD_SONGS: str = "✅ Песни успешно добавлены"
    SUCCESS_ADD_ALBUM: str = "✅ Альбом успешно добавлен"

    # коды ошибок при запросе
    ERROR_SHOW_EXECUTOR: str = (
        "❌ Произошла ошибка при загрузке исполнителей с альбомами"
    )
    ERROR_SHOW_ALBUM_WITH_SONGS: str = (
        "❌ Произошла ошибка при загрузке альбома с песнями"
    )
    ERROR_BACK_EXECUTOR: str = "❌ Произошла ошибка при возвращении к исполнителю"
    ERROR_PLAY_SONG: str = "❌ Произошла ошибка при загрузке песни"
    ERROR_INFO_EXECUTOR: str = (
        "❌ Произошла ошибка при получении информации об исполнителе"
    )
    ERROR_INFO_ALBUM: str = "❌ Произошла ошибка при получении информации об альбоме"
    ERROR_POSITIONS_SONGS: str = "❌ Произошла ошибка при получении позиций песен"
    ERROR_MENU_SONGS_DELETE: str = (
        "❌ Произошла ошибка при получении позиций песен для их удаления"
    )

    ERROR_UPDATE_PHOTO_EXECUTOR: str = (
        "❌ Произошла ошибка при обновлении фото исполнителя"
    )
    ERROR_UPDATE_PHOTO_ALBUM: str = "❌ Произошла ошибка при обновлении фото альбома"
    ERROR_UPDATE_EXECUTOR_NAME: str = (
        "❌ Произошла ошибка при обновлении имени исполнителя"
    )
    ERROR_UPDATE_EXECUTOR_COUNTRY: str = (
        "❌ Произошла ошибка при обновлении страны исполнителя"
    )
    ERROR_UPDATE_ALBUM_TITLE: str = "❌ Произошла ошибка при обновлении имени альбома"
    ERROR_UPDATE_ALBUM_YEAR: str = (
        "❌ Произошла ошибка при обновлении года выпуска альбома"
    )
    ERROR_UPDATE_EXECUTOR_GENRES: str = (
        "❌ Произошла ошибка при обновлении жанров исполнителя"
    )
    ERROR_UPDATE_TITLE_SONG: str = "❌ Произошла ошибка при обновлении имени песни"

    ERROR_DELETE_EXECUTOR: str = "❌ Произошла ошибка при удалении исполнителя"
    ERROR_DELETE_ALBUM: str = "❌ Произошла ошибка при удалении альбома"
    ERROR_DELETE_SONGS: str = "❌ Произошла ошибка при удалении песен"

    ERROR_ADD_EXECUTOR: str = "❌ Произошла ошибка добавлении исполнителя"
    ERROR_ADD_SONGS: str = "❌ Произошла ошибка при добавлении песен в альбом"
    ERROR_ADD_ALBUM: str = "❌ Произошла ошибка при добавлении альбома"

    # коды когда при запросах ничего не найдено
    NOT_FOUND_EXECUTORS: str = "⚠ Не найденно ни одного исполнителя"
    NOT_FOUND_EXECUTOR: str = "⚠ Исполнитель не найден"
    NOT_FOUND_ALBUM: str = "⚠ Альбом не найден"
    NOT_FOUND_SONGS: str = "⚠ У альбома нет загруженных песен"
    NOT_FOUND_TITLE_SONG_POSITION: str = "⚠ В альбоме нет песен с указанной позицией"

    CANCEL_OPERATION: str = "❌ Отменены все действия"
