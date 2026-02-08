from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.view_model import AlbumResponse, SongResponse
from app.bot.modules.admin.childes.base_music.filters import (
    BackExecutorCallback,
    BasePlaySongCallback,
    BaseDeleteExecutorCallback,
    BaseMusicCallback,
    BaseDeleteAlbumCallback,
    ConfirmBaseDeleteExecutorCallback,
    ConfirmBaseDeleteAlbumCallback,
    BaseDeleteSongMenuCallback,
    BaseButtonDeleteSongCallback,
    ConfirmBaseDeleteSongCallback,
    CancelBaseDeleteSongCallback,
    CompleteBaseDeleteSongCallback,
)
from app.bot.modules.admin.filters import (
    BackAdminMenuCallback,
)
from app.bot.modules.admin.childes.base_music.keyboards.response import KeyboardResponse


def show_one_album_songs_with_base_executor(
    list_songs: List[SongResponse],
    executor_id: int,
    album_id: int,
) -> InlineKeyboardMarkup:

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if list_songs:
        for song in list_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data=BasePlaySongCallback(
                        position=song.position, album_id=song.album_id
                    ).pack(),
                )
            )
    if list_songs:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.DELETE_SONGS.value,
                callback_data=BaseDeleteSongMenuCallback(
                    album_id=album_id,
                ).pack(),
            )
        )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_ALBUM.value,
            callback_data=BaseDeleteAlbumCallback(
                executor_id=executor_id, album_id=album_id
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS.value,
            callback_data=BackExecutorCallback(executor_id=executor_id).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL.value,
            callback_data=BackAdminMenuCallback().pack(),
        )
    )
    return inline_kb.as_markup()


def show_base_executor_collections(
    list_albums: List[AlbumResponse],
    executor_id: int,
) -> InlineKeyboardMarkup:

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if not list_albums:
        inline_kb.row(
            InlineKeyboardButton(
                text="У исполнителя нет загруженных альбомов", callback_data="not album"
            )
        )
    else:
        for album in list_albums:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"({album.year}) {album.title}",
                    callback_data=BaseMusicCallback(
                        executor_id=album.executor_id,
                        album_id=album.album_id,
                    ).pack(),
                )
            )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_EXECUTOR.value,
            callback_data=BaseDeleteExecutorCallback(
                executor_id=executor_id,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL.value,
            callback_data=BackAdminMenuCallback().pack(),
        )
    )

    return inline_kb.as_markup()


def get_confirmation_delete_executor_button(
    executor_id: int,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=ConfirmBaseDeleteExecutorCallback(
                executor_id=executor_id
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=ConfirmBaseDeleteExecutorCallback(executor_id=None).pack(),
        )
    )
    return inline_kb.as_markup()


def get_confirmation_delete_album_button(
    album_id: int,
    executor_id: int,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=ConfirmBaseDeleteAlbumCallback(
                executor_id=executor_id, album_id=album_id
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=ConfirmBaseDeleteAlbumCallback(
                executor_id=None,
                album_id=None,
            ).pack(),
        )
    )
    return inline_kb.as_markup()


def get_menu_song_delete(
    list_songs: List[SongResponse],
    album_id: int,
    delete_songs: set = None,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for song in list_songs:
        if not delete_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"☑ {song.position}. {song.title}",
                    callback_data=BaseButtonDeleteSongCallback(
                        album_id=song.album_id,
                        song_id=song.song_id,
                    ).pack(),
                )
            )
        else:
            delete_img = "✅" if song.song_id in delete_songs else "☑ "
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{delete_img} {song.position}. {song.title}",
                    callback_data=BaseButtonDeleteSongCallback(
                        album_id=song.album_id,
                        song_id=song.song_id,
                    ).pack(),
                )
            )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CONFIRM_THE_DELETION_OF_SONGS.value,
            callback_data=ConfirmBaseDeleteSongCallback(album_id=album_id).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=CancelBaseDeleteSongCallback().pack(),
        )
    )

    return inline_kb.as_markup()


def get_confirmation_delete_song_button():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=CompleteBaseDeleteSongCallback().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=CancelBaseDeleteSongCallback().pack(),
        )
    )
    return inline_kb.as_markup()
