from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from domain.entities.response import (
    CollectionSongsResponse,
    ExecutorPageResponse,
    SongResponse,
    AlbumPageResponse,
)
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.filters import (
    ShowAlbumExecutor,
    AddCallbackDataFilters,
    ScrollingCallbackDataFilters,
    UpdateCallbackDataFilters,
    DeleteCallbackDataFilters,
    BackMenuUserPanel,
    PlaySongsCollectionSongs,
)
from infrastructure.aiogram.filters import ScrollingCallbackDataFilters
from infrastructure.aiogram.keyboards.utils import build_pages


### инлайн клавиатуры для сборника песен


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


#### инланй клавиатуры для глобальной библиотеки


def show_executor_global_collections(
    limit_albums: int,
    album_position: int,
    executor: ExecutorPageResponse = None,
):

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    if not executor:  # если на странице нет исполнителей
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.NOT_FOUND_EXECUTORS,
                callback_data="NOT_FOUND_EXECUTORS",
            )
        )

    else:
        albums = executor.albums
        count_albums = len(albums)

        albums = albums[album_position : album_position + limit_albums]
        executor_id = executor.id
        user_id = executor.user_id
        total_pages = executor.total_pages
        current_page = executor.current_page

        if not albums:
            inline_kb.row(
                InlineKeyboardButton(
                    text=KeyboardResponse.NOT_FOUND_ALBUMS,
                    callback_data="NOT_FOUND_ALBUMS",
                )
            )
        else:
            for album in albums:
                inline_kb.row(
                    InlineKeyboardButton(
                        text=f"({album.year}) {album.title}",
                        callback_data=ShowAlbumExecutor(
                            album_id=album.id,
                            user_id=user_id,
                            executor_id=executor_id,
                            current_page_executor=current_page,
                        ).pack(),
                    )
                )
            buttons = []
            has_prev = album_position > 0
            has_next = album_position + limit_albums < count_albums
            if has_prev:
                buttons.append(
                    InlineKeyboardButton(
                        text=KeyboardResponse.BACK_BUTTON,
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorGlobalLibrary(
                            executor_id=executor_id,
                            user_id=user_id,
                            current_page_executor=current_page,
                            position=album_position,
                            offset=-limit_albums,
                        ).pack(),
                    )
                )
            if has_next:
                buttons.append(
                    InlineKeyboardButton(
                        text=KeyboardResponse.FORWARD_BUTTON,
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorGlobalLibrary(
                            executor_id=executor_id,
                            user_id=user_id,
                            current_page_executor=current_page,
                            position=album_position,
                            offset=limit_albums,
                        ).pack(),
                    )
                )
            inline_kb.row(*buttons)

            pages = build_pages(current=current_page, total=total_pages)
            for index, page in enumerate(pages, start=1):
                page_data = f"[{page}]" if page == current_page else page
                if index == 1:
                    inline_kb.row(
                        InlineKeyboardButton(
                            text=f"{page_data}",
                            callback_data=ScrollingCallbackDataFilters.ExecutorPageGlobalLibrary(
                                executor_id=executor_id,
                                current_page_executor=page,
                                user_id=user_id,
                            ).pack(),
                        )
                    )
                else:
                    inline_kb.add(
                        InlineKeyboardButton(
                            text=f"{page_data}",
                            callback_data=ScrollingCallbackDataFilters.ExecutorPageGlobalLibrary(
                                executor_id=executor_id,
                                current_page_executor=page,
                                user_id=user_id,
                            ).pack(),
                        )
                    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()


def show_album_collections(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if not songs:  # в альбоме нет песен
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.NOT_FOUND_SONGS,
                callback_data="NOT_FOUND_SONGS",
            )
        )

    else:
        songs = album.songs
        number_of_songs = len(songs)
        executor_id = album.executor_id
        album_id = album.id

        songs = songs[song_position : song_position + limit_songs]
        current_page_executor: int = album.current_page_executor

        for song in songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data="data",
                ),
            )
        buttons = []
        has_prev = song_position > 0
        has_next = song_position + limit_songs < number_of_songs
        if has_prev:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumGlobalLibrary(
                        position=song_position,
                        offset=-limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                    ).pack(),
                )
            )
        if has_next:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumGlobalLibrary(
                        position=song_position,
                        offset=limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                    ).pack(),
                )
            )
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )
    return inline_kb.as_markup()
