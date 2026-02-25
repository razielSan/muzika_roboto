from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from app.bot.view_model import AlbumResponse, SongResponse
from app.bot.filters.admin_filters import (
    AdminBackExecutorCallback,
    AdminPlaySongCallback,
    AdminDeleteExecutorCallback,
    AdminMusicCallback,
    AdminDeleteAlbumCallback,
    AdminConfirmDeleteExecutorCallback,
    AdminConfirmDeleteAlbumCallback,
    AdminDeleteSongMenuCallback,
    AdminButtonDeleteSongCallback,
    AdminConfirmDeleteSongCallback,
    AdminCancelDeleteSongCallback,
    AdminCompleteDeleteSongCallback,
    AdminScrollingSongsCallback,
    AdminScrollingExecutorsCallback,
    AdminScrollingAlbumsCallback,
    AdminUpdatePhotoExecutorCallback,
    AdminUpdatePhotoAlbumCallback,
    AdminUpdateExecutorNameCallback,
    AdminUpdateExecutorCountryCallback,
    AdminUpdateAlbumTitleCallback,
    AdminUpdateAlbumYearCallback,
    AdminUpdateExecutorGenresCallback,
    AdminScrollingSongsMenuDeleteCallback,
    AdminAddSongsCallback,
    AdminAddAlbumCallback,
    AdminUpdateSongTitleCallback,
    BackAdminMenuCallback,
)

from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.keyboards.utils import build_pages


def show_one_album_songs_with_base_executor(
    list_songs: List[SongResponse],
    executor_id: int,
    album_id: int,
    current_page_executor: int,
    count_pages_executor: int,
    len_list_songs: int = 0,
    limit_songs: int = 5,
    song_position: int = 0,
) -> InlineKeyboardMarkup:
    """Отрисовывает инлайн меню альбома с песнями."""

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if list_songs:  # для отображения песен
        for song in list_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data=AdminPlaySongCallback(
                        position=song.position, album_id=song.album_id
                    ).pack(),
                )
            )

    if list_songs:  # для пролистывания песен
        has_prev = song_position > 0
        has_next = song_position + limit_songs < len_list_songs

        buttons = []

        if has_prev:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON.value,
                    callback_data=AdminScrollingSongsCallback(
                        album_id=album_id,
                        executor_id=executor_id,
                        position=song_position,
                        current_page_executor=current_page_executor,
                        count_pages_executor=count_pages_executor,
                        offset=-limit_songs,
                    ).pack(),
                )
            )

        if has_next:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON.value,
                    callback_data=AdminScrollingSongsCallback(
                        album_id=album_id,
                        executor_id=executor_id,
                        position=song_position,
                        offset=limit_songs,
                        current_page_executor=current_page_executor,
                        count_pages_executor=count_pages_executor,
                    ).pack(),
                )
            )

        if buttons:
            inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS.value,
            callback_data=AdminAddSongsCallback(
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
                executor_id=executor_id,
            ).pack(),
        )
    )

    if list_songs:  # для изменения имени песни
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_TITLE_SONG.value,
                callback_data=AdminUpdateSongTitleCallback(
                    executor_id=executor_id,
                    album_id=album_id,
                    current_page_executor=current_page_executor,
                    count_pages_executor=count_pages_executor,
                ).pack(),
            )
        )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_PHOTO_ALBUM.value,
            callback_data=AdminUpdatePhotoAlbumCallback(
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_TITLE_ALBUM.value,
            callback_data=AdminUpdateAlbumTitleCallback(
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_YEAR_ALBUM.value,
            callback_data=AdminUpdateAlbumYearCallback(
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )

    if list_songs:  # для удаления песен
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.DELETE_SONGS.value,
                callback_data=AdminDeleteSongMenuCallback(
                    album_id=album_id,
                    executor_id=executor_id,
                    current_page_executor=current_page_executor,
                    count_pages_executor=count_pages_executor,
                ).pack(),
            )
        )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_ALBUM.value,
            callback_data=AdminDeleteAlbumCallback(
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS.value,
            callback_data=AdminBackExecutorCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
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


def show_base_executor_collections(
    list_albums: List[AlbumResponse],
    executor_id: int,
    count_pages_executor: int,
    current_page_executor: int,
    limit_albums: int,
    album_position: int,
    len_list_albums: int,
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
                    callback_data=AdminMusicCallback(
                        executor_id=album.executor_id,
                        album_id=album.album_id,
                        current_page_executor=current_page_executor,
                        count_pages_executor=count_pages_executor,
                    ).pack(),
                )
            )
        has_prev = album_position > 0
        has_next = album_position + limit_albums < len_list_albums
        buttons = []
        if has_prev:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON.value,
                    callback_data=AdminScrollingAlbumsCallback(
                        executor_id=executor_id,
                        position=album_position,
                        offset=-limit_albums,
                        current_page_executor=current_page_executor,
                    ).pack(),
                )
            )

        if has_next:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON.value,
                    callback_data=AdminScrollingAlbumsCallback(
                        executor_id=executor_id,
                        position=album_position,
                        offset=limit_albums,
                        current_page_executor=current_page_executor,
                    ).pack(),
                )
            )
        if buttons:
            inline_kb.row(*buttons)

    if count_pages_executor == 1:
        pass

    else:
        list_buttons = build_pages(
            current=current_page_executor,
            total=count_pages_executor,
        )
        for digit in list_buttons:
            if digit == 1:
                inline_kb.row(
                    InlineKeyboardButton(
                        text="[ 1 ]" if digit == current_page_executor else str(digit),
                        callback_data=AdminScrollingExecutorsCallback(
                            current_page=digit,
                        ).pack(),
                    )
                )
            else:
                inline_kb.add(
                    InlineKeyboardButton(
                        text=f"[ {digit} ]"
                        if digit == current_page_executor
                        else str(digit),
                        callback_data=AdminScrollingExecutorsCallback(
                            current_page=digit,
                        ).pack(),
                    )
                )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_ALBUM.value,
            callback_data=AdminAddAlbumCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_PHOTO_EXECUTOR.value,
            callback_data=AdminUpdatePhotoExecutorCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_NAME_EXECUTOR.value,
            callback_data=AdminUpdateExecutorNameCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_COUNTRY_EXECUTOR.value,
            callback_data=AdminUpdateExecutorCountryCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_EXECUTOR_GENRES.value,
            callback_data=AdminUpdateExecutorGenresCallback(
                executor_id=executor_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_EXECUTOR.value,
            callback_data=AdminDeleteExecutorCallback(
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
            callback_data=AdminConfirmDeleteExecutorCallback(
                executor_id=executor_id
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=AdminConfirmDeleteExecutorCallback(executor_id=None).pack(),
        )
    )
    return inline_kb.as_markup()


def get_confirmation_delete_album_button(
    album_id: int,
    executor_id: int,
    current_page_executor: int,
    count_pages_executor: int,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=AdminConfirmDeleteAlbumCallback(
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=AdminConfirmDeleteAlbumCallback(
                executor_id=None,
                album_id=None,
                current_page_executor=None,
                count_pages_executor=None,
            ).pack(),
        )
    )
    return inline_kb.as_markup()


def get_menu_song_delete(
    list_songs: List[SongResponse],
    album_id: int,
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
                    callback_data=AdminButtonDeleteSongCallback(
                        album_id=song.album_id,
                        song_id=song.song_id,
                        position=song_position,
                    ).pack(),
                )
            )
        else:
            delete_img = "✅" if song.song_id in delete_songs else "☑ "
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{delete_img} {song.position}. {song.title}",
                    callback_data=AdminButtonDeleteSongCallback(
                        album_id=song.album_id,
                        song_id=song.song_id,
                        position=song_position,
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
                callback_data=AdminScrollingSongsMenuDeleteCallback(
                    album_id=album_id, position=song_position, offset=-limit_songs
                ).pack(),
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON.value,
                callback_data=AdminScrollingSongsMenuDeleteCallback(
                    album_id=album_id, position=song_position, offset=limit_songs
                ).pack(),
            )
        )

    if buttons:
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CONFIRM_THE_DELETION_OF_SONGS.value,
            callback_data=AdminConfirmDeleteSongCallback(album_id=album_id).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=AdminCancelDeleteSongCallback().pack(),
        )
    )

    return inline_kb.as_markup()


def get_confirmation_delete_song_button():
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=AdminCompleteDeleteSongCallback().pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_THE_DELETION_OF_SONGS.value,
            callback_data=AdminCancelDeleteSongCallback().pack(),
        )
    )
    return inline_kb.as_markup()
