from typing import Optional

from aiogram.filters.callback_data import CallbackData


class AdminBackExecutorCallback(CallbackData, prefix="admin_back_executor"):
    """Каллбэк для сценария возврата, по нажатию кнопки, назад к исполнителю c альбомами."""

    executor_id: int
    current_page_executor: int


class AdminMusicCallback(CallbackData, prefix="admin_base_music"):
    executor_id: int
    album_id: int
    current_page_executor: int


class AdminPlaySongCallback(CallbackData, prefix="admin_play_song"):
    position: int
    album_id: int


class AdminDeleteExecutorCallback(CallbackData, prefix="admin_del_executor"):
    executor_id: int


class AdminConfirmDeleteExecutorCallback(
    CallbackData, prefix="confirm_admin_del_executor"
):
    executor_id: Optional[int]


class AdminDeleteAlbumCallback(CallbackData, prefix="admin_del_album"):
    executor_id: int
    album_id: int


class AdminConfirmDeleteAlbumCallback(CallbackData, prefix="confirm_admin_del_album"):
    executor_id: Optional[int]
    album_id: Optional[int]


class AdminDeleteSongMenuCallback(CallbackData, prefix="admin_del_song_menu"):
    """Каллбэк для сценрая показа инлайн меню выбора песен для удаления."""

    album_id: int


class AdminButtonDeleteSongCallback(CallbackData, prefix="admin_button_del_song"):
    album_id: int
    song_id: int
    position: int


class AdminConfirmDeleteSongCallback(CallbackData, prefix="confirm_admin_del_songs"):
    album_id: int


class AdminCancelDeleteSongCallback(CallbackData, prefix="cancel_admin_del_songs"):
    """Каллбэк для сценария отмены удаления песен."""
    pass


class AdminCompleteDeleteSongCallback(CallbackData, prefix="compl_admin_del_songs"):
    """Каллбэк для сценрая удаления песен после подтверждения."""

    pass


class AdminScrollingSongsCallback(CallbackData, prefix="scrolling_admin_songs"):
    """Каллбэк для сценария пролистывания песен в альбоме."""

    executor_id: int
    album_id: int
    position: int
    offset: int
    current_page_executor: int
    

class AdminScrollingSongsMenuDeleteCallback(CallbackData, prefix="scrolling_del_admin_songs"):
    """Каллбэк для сценария пролистывания песен в меню удаления песен."""

    album_id: int
    position: int
    offset: int


class AdminScrollingAlbumsCallback(CallbackData, prefix="scrolling_admin_albums"):
    """Каллбэк для сценария пролистывания альбомов."""

    executor_id: int
    position: int
    offset: int
    current_page_executor: int


class AdminScrollingExecutorsCallback(
    CallbackData, prefix="scorolling_admin_executors"
):
    """Каллбэк для сценария пролистывания исполнителей."""

    current_page: int


class AdminUpdatePhotoExecutorCallback(
    CallbackData, prefix="update_admin_executor_photo"
):
    executor_id: int


class AdminUpdatePhotoAlbumCallback(CallbackData, prefix="update_admin_album_photo"):
    executor_id: int
    album_id: int


class AdminUpdateExecutorNameCallback(
    CallbackData, prefix="update_admin_executor_name"
):
    executor_id: int


class AdminUpdateExecutorCountryCallback(
    CallbackData, prefix="update_admin_executor_country"
):
    executor_id: int


class AdminUpdateAlbumTitleCallback(CallbackData, prefix="update_admin_album_title"):
    executor_id: int
    album_id: int


class AdminUpdateAlbumYearCallback(CallbackData, prefix="update_admin_album_year"):
    executor_id: int
    album_id: int


class AdminUpdateExecutorGenresCallback(
    CallbackData, prefix="update_admin_executor_genres"
):
    executor_id: int
