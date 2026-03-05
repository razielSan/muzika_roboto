from typing import List
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    AddCallbackDataFilters,
    ScrollingCallbackDataFilters,
    UpdateCallbackDataFilters,
    DeleteCallbackDataFilters,
    BackMenuUserPanel,
    PlaySongsCollectionSongs,
)
from domain.entities.response import CollectionSongsResponse


def get_buttons_for_song_collection_empty_user():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.SongCollectionSongs().pack(),
        )
    )
    return inline_kb.as_markup()


def get_buttons_for_song_collection_user(
    colellection_songs: List[CollectionSongsResponse],
    len_collection_songs: int,
    song_position: int = 0,
    limit_songs: int = 1,
):

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for song in colellection_songs:
        inline_kb.row(
            InlineKeyboardButton(
                text=f"{song.position}. {song.title}",
                callback_data=PlaySongsCollectionSongs(
                    song_id=song.id,
                ).pack(),
            )
        )

    buttons = []
    has_prev = song_position > 0
    has_next = song_position + limit_songs < len_collection_songs

    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_BUTTON,
                callback_data=ScrollingCallbackDataFilters.SongCollectionSongs(
                    position=song_position, offset=-limit_songs
                ).pack(),
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON,
                callback_data=ScrollingCallbackDataFilters.SongCollectionSongs(
                    position=song_position, offset=limit_songs
                ).pack(),
            )
        )

    inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.SongCollectionSongs().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_PHOTO_COLLECTION_SONGS,
            callback_data=UpdateCallbackDataFilters.UserCollectionSongsPhotoFileId().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_TITLE_SONG,
            callback_data=UpdateCallbackDataFilters.SongTitleCollectionSongs().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_SONGS,
            callback_data=DeleteCallbackDataFilters.SongCollectionSongs().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )
    return inline_kb.as_markup()


def get_menu_songs_collection_songs_delete(
    list_songs: List[CollectionSongsResponse],
    song_position: int = 0,
    len_list_songs=0,
    limit_songs=5,
    delete_songs: set = None,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for song in list_songs:
        if not delete_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"☑ {song.position}. {song.title}",
                    callback_data=DeleteCallbackDataFilters.ButtonsDeleteSongColletionSongs(
                        song_id=song.id, position=song_position
                    ).pack(),
                )
            )
        else:
            delete_img = "✅" if song.id in delete_songs else "☑ "
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{delete_img} {song.position}. {song.title}",
                    callback_data=DeleteCallbackDataFilters.ButtonsDeleteSongColletionSongs(
                        song_id=song.id, position=song_position
                    ).pack(),
                )
            )

    has_prev = song_position > 0
    has_next = song_position + limit_songs < len_list_songs
    buttons = []

    if has_prev:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_BUTTON.value,
                callback_data=ScrollingCallbackDataFilters.DeleteMenuSongColletionSongs(
                    position=song_position, offset=-limit_songs
                ).pack(),
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON.value,
                callback_data=ScrollingCallbackDataFilters.DeleteMenuSongColletionSongs(
                    position=song_position, offset=limit_songs
                ).pack(),
            )
        )

    if buttons:
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CONFIRM_THE_DELETION_OF_SONGS.value,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteSongCollectionSongs().pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()


def get_confirmation_delete_song_button():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=DeleteCallbackDataFilters.CompleteDeleteSongCollectionSongs().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=BackMenuUserPanel().pack(),
        )
    )
    return inline_kb.as_markup()
