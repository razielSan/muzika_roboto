from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    AddCallbackDataFilters,
    ScrollingCallbackDataFilters,
)
from domain.entities.response import CollectionSongResponse


def get_buttons_for_song_collection_empty_user():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.CollectionSong().pack(),
        )
    )
    return inline_kb.as_markup()


def get_buttons_for_song_collection_user(
    colellection_songs: List[CollectionSongResponse],
    len_collection_songs: int,
    song_position: int = 0,
    limit_songs: int = 1,
):

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for song in colellection_songs:
        inline_kb.row(
            InlineKeyboardButton(
                text=f"{song.position}. {song.title}", callback_data="ok"
            )
        )

    buttons = []
    has_prev = song_position > 0
    has_next = song_position + limit_songs < len_collection_songs

    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_BUTTON,
                callback_data=ScrollingCallbackDataFilters.CollectionSong(
                    position=song_position, offset=-limit_songs
                ).pack(),
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON,
                callback_data=ScrollingCallbackDataFilters.CollectionSong(
                    position=song_position, offset=limit_songs
                ).pack(),
            )
        )

    inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.CollectionSong().pack(),
        )
    )
    return inline_kb.as_markup()
