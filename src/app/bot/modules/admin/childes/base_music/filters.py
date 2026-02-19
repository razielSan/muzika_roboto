from typing import Optional

from aiogram.filters.callback_data import CallbackData


class AdminBackExecutorCallback(CallbackData, prefix="admin_back_executor"):
    """Каллбэк для сценария возврата, по нажатию кнопки, назад к исполнителю c альбомами."""

    executor_id: int
    current_page_executor: int


class AdminMusicCallback(CallbackData, prefix="admin_base_music"):
    """Каллбэк для сценаря показа альбома со списокм песен"""
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminPlaySongCallback(CallbackData, prefix="admin_play_song"):
    position: int
    album_id: int


class AdminDeleteExecutorCallback(CallbackData, prefix="admin_del_executor"):
    executor_id: int


class AdminConfirmDeleteExecutorCallback(
    CallbackData, prefix="admin_confirm_del_executor"
):
    executor_id: Optional[int]


class AdminDeleteAlbumCallback(CallbackData, prefix="admin_del_album"):
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminConfirmDeleteAlbumCallback(CallbackData, prefix="admin_confirm_del_album"):
    """Каллбэк для сценаря подтверждения или отмены удаления альбома"""
    executor_id: Optional[int]
    album_id: Optional[int]
    current_page_executor: Optional[int]
    count_pages_executor: Optional[int]


class AdminDeleteSongMenuCallback(CallbackData, prefix="admin_del_song_menu"):
    """Каллбэк для сценрая показа инлайн меню выбора песен для удаления."""

    album_id: int
    executor_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminButtonDeleteSongCallback(CallbackData, prefix="admin_button_del_song"):
    album_id: int
    song_id: int
    position: int


class AdminConfirmDeleteSongCallback(CallbackData, prefix="admin_confirm_del_songs"):
    """Каллбэк для сценаря подтверждения или отмены удаления песен"""
    album_id: int


class AdminCancelDeleteSongCallback(CallbackData, prefix="admin_cancel_del_songs"):
    """Каллбэк для сценария отмены удаления песен."""

    pass


class AdminCompleteDeleteSongCallback(CallbackData, prefix="admin_compl_del_songs"):
    """Каллбэк для сценапмя удаления песен после подтверждения."""

    pass


class AdminScrollingSongsCallback(CallbackData, prefix="admin_scrolling_songs"):
    """Каллбэк для сценария пролистывания песен в альбоме."""

    executor_id: int
    album_id: int
    position: int
    offset: int
    current_page_executor: int
    count_pages_executor: int


class AdminScrollingSongsMenuDeleteCallback(
    CallbackData, prefix="admin_scrolling_del_songs"
):
    """Каллбэк для сценария пролистывания песен в меню удаления песен."""

    album_id: int
    position: int
    offset: int


class AdminScrollingAlbumsCallback(CallbackData, prefix="admin_scrolling_albums"):
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
    current_page_executor: int
    count_pages_executor: int


class AdminUpdatePhotoAlbumCallback(CallbackData, prefix="admin_update_album_photo"):
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminUpdateExecutorNameCallback(
    CallbackData, prefix="admin_update_executor_name"
):
    executor_id: int


class AdminUpdateExecutorCountryCallback(
    CallbackData, prefix="admin_update_executor_country"
):
    executor_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminUpdateAlbumTitleCallback(CallbackData, prefix="admin_update_album_title"):
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminUpdateAlbumYearCallback(CallbackData, prefix="admin_update_album_year"):
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminUpdateExecutorGenresCallback(
    CallbackData, prefix="admin_update_executor_genres"
):
    executor_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminAddSongsCallback(CallbackData, prefix="admin_add_songs"):
    executor_id: int
    album_id: int
    current_page_executor: int
    count_pages_executor: int


class AdminAddAlbumCallback(CallbackData, prefix="admin_add_album"):
    executor_id: int
    current_page_executor: int
    count_pages_executor: int
