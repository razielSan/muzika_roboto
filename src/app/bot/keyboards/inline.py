from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.bot.view_model import SongResponse, AlbumResponse
from app.bot.modules.admin.childes.base_music.filters import (
    BackExecutorCallback,
    BaseMusicCallback,
    PlaySongCallback,
)


def show_base_executor_collections(
    list_albums: List[AlbumResponse],
) -> InlineKeyboardMarkup:

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

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
    return inline_kb.as_markup(resize_keyboard=True)


def show_one_album_songs(
    list_songs: List[SongResponse],
    executor_id: int,
) -> InlineKeyboardMarkup:

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if list_songs:
        for song in list_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data=PlaySongCallback(
                        position=song.position, album_id=song.album_id
                    ).pack(),
                )
            )
    inline_kb.row(
        InlineKeyboardButton(
            text="⬅ Назад к альбомам",
            callback_data=BackExecutorCallback(executor_id=executor_id).pack(),
        )
    )
    return inline_kb.as_markup(resize_keyboard=True)
