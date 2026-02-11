from enum import Enum


class KeyboardResponse(Enum):
    YES: str = "[ Да ]"
    NO: str = "[ Нет ]"
    CANCEL_THE_DELETION_OF_SONGS: str = "ОТМЕНИТЬ УДАЛЕНИЕ ПЕСЕН"
    CONFIRM_THE_DELETION_OF_SONGS: str = "ПОДТВЕРДИТЬ УДАЛЕНИЕ ПЕСЕН"
    BACK_TO_THE_ADMIN_PANEL: str = "⬅ Назад к админ панели"
    BACK_TO_ALBUMS: str = "⬅ Назад к альбомам"
    DELETE_SONGS: str = "🗑 Удалить Песни"
    DELETE_ALBUM: str = "🗑 Удалить Альбом"
    DELETE_EXECUTOR: str = "🗑 Удалить Исполнителя"
    BACK_BUTTON: str = "⬅ Назад"
    FORWARD_BUTTON: str = "Вперед ➡"


LIMIT_SONGS: int = 5
LIMIT_ALBUMS: int = 5
