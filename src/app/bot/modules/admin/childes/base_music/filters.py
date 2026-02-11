from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BackExecutorCallback(CallbackData, prefix="admin_back_executor"):
    """Каллбэк для сценария возврата, по нажатию кнопки, назад к исполнителю c альбомами."""

    executor_id: int
    current_page_executor: int


class BaseMusicCallback(CallbackData, prefix="admin_base_music"):
    executor_id: int
    album_id: int
    current_page_executor: int


class BasePlaySongCallback(CallbackData, prefix="admin_play_song"):
    position: int
    album_id: int


class BaseDeleteExecutorCallback(CallbackData, prefix="admin_del_executor"):
    executor_id: int


class ConfirmBaseDeleteExecutorCallback(
    CallbackData, prefix="confirm_admin_del_executor"
):
    executor_id: Optional[int]


class BaseDeleteAlbumCallback(CallbackData, prefix="admin_del_album"):
    executor_id: int
    album_id: int


class ConfirmBaseDeleteAlbumCallback(CallbackData, prefix="confirm_admin_del_album"):
    executor_id: Optional[int]
    album_id: Optional[int]


class BaseDeleteSongMenuCallback(CallbackData, prefix="admin_del_song_menu"):
    """Каллбэк для сценрая показа инлайн меню выбора песен для удаления."""

    album_id: int


class BaseButtonDeleteSongCallback(CallbackData, prefix="admin_button_del_song"):
    album_id: int
    song_id: int


class ConfirmBaseDeleteSongCallback(CallbackData, prefix="confirm_admin_del_songs"):
    album_id: int


class CancelBaseDeleteSongCallback(CallbackData, prefix="cancel_admin_del_songs"):
    """Каллбэк для сценария отмены удаления песен."""

    pass


class CompleteBaseDeleteSongCallback(CallbackData, prefix="compl_admin_del_songs"):
    """Каллбэк для сценрая удаления песен после подтверждения."""

    pass


class ScrollingSongsCallback(CallbackData, prefix="scrolling_songs"):
    """Каллбэк для сценария пролистывания песен в альбоме."""

    executor_id: int
    album_id: int
    position: int
    offset: int
    current_page_executor: int


class ScrollingAlbumsCallback(CallbackData, prefix="scrolling_albums"):
    """Каллбэк для сценария пролистывания альбомов."""

    executor_id: int
    position: int
    offset: int
    current_page_executor: int


class ScrollingEXecutorsCallback(CallbackData, prefix="scorolling_executors"):
    """Каллбэк для сценария пролистывания исполнителей."""

    current_page: int
