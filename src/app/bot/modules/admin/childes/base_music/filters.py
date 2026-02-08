from typing import Optional

from aiogram.filters.callback_data import CallbackData


class BackExecutorCallback(CallbackData, prefix="admin_back_executor"):
    executor_id: int


class BaseMusicCallback(CallbackData, prefix="admin_base_music"):
    executor_id: int
    album_id: int


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
    album_id: int


class BaseButtonDeleteSongCallback(CallbackData, prefix="admin_button_del_song"):
    album_id: int
    song_id: int


class ConfirmBaseDeleteSongCallback(CallbackData, prefix="confirm_admin_del_songs"):
    album_id: int


class CancelBaseDeleteSongCallback(CallbackData, prefix="cancel_admin_del_songs"):
    pass


class CompleteBaseDeleteSongCallback(CallbackData, prefix="compl_admin_del_songs"):
    pass
