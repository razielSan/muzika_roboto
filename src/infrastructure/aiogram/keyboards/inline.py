from typing import List, Optional

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
    BackExecutorPage,
    PlaySongsCollectionSongs,
    PlaySongsAlbums,
    SyncExecutor,
    DesyncExecutor,
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
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
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
            text=KeyboardResponse.CONFIRM_DELETE.value,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteSongCollectionSongs().pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_DELETE.value,
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
            text=KeyboardResponse.CANCEL_DELETE.value,
            callback_data=BackMenuUserPanel().pack(),
        )
    )
    return inline_kb.as_markup()


#### инланй клавиатуры для глобальной библиотеки


def show_executor_global_collections(
    limit_albums: int,
    album_position: int,
    executor: ExecutorPageResponse = None,
    is_sync_executor=True,
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

        album_position = max(0, album_position)  # страховка
        albums = albums[album_position : album_position + limit_albums]
        executor_id = executor.id
        user_id = executor.current_user_id
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
                            album_position=album_position,
                            album_id=album.id,
                            user_id=user_id,
                            executor_id=executor_id,
                            current_page_executor=current_page,
                            is_global_executor=executor.is_global,
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
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
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
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
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

            # для избежания выхода за границы
            back_button_page = max(1, current_page - 1)
            forward_button_page = min(total_pages, current_page + 1)
            if pages:  # если исполнителей больше одного
                inline_kb.row(
                    InlineKeyboardButton(
                        text="⬅️",
                        callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                            executor_id=executor_id,
                            current_page_executor=back_button_page,
                            user_id=user_id,
                        ).pack(),
                    )
                )
                for index, page in enumerate(pages, start=1):
                    page_data = f"[{page}]" if page == current_page else page
                    inline_kb.add(
                        InlineKeyboardButton(
                            text=f"{page_data}",
                            callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                                executor_id=executor_id,
                                current_page_executor=page,
                                user_id=user_id,
                            ).pack(),
                        )
                    )
                inline_kb.add(
                    InlineKeyboardButton(
                        text="➡️",
                        callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                            executor_id=executor_id,
                            current_page_executor=forward_button_page,
                            user_id=user_id,
                        ).pack(),
                    )
                )

            if is_sync_executor:  # для синхронизации
                inline_kb.row(
                    InlineKeyboardButton(
                        text=KeyboardResponse.SYNC_EXECUTOR,
                        callback_data=SyncExecutor(executor_id=executor_id).pack(),
                    )
                )
            else:
                inline_kb.row(
                    InlineKeyboardButton(
                        text=KeyboardResponse.DESYNC_EXECUTOR,
                        callback_data=DesyncExecutor(executor_id=executor_id).pack(),
                    )
                )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
            callback_data=BackMenuUserPanel().pack(),
        )
    )

    return inline_kb.as_markup()


# инлайн клавиатуры для пользовательской библиотеки


def show_executor_user_collections(
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

        album_position = max(0, album_position)  # страховка
        albums = albums[album_position : album_position + limit_albums]
        executor_id = executor.id
        user_id = executor.current_user_id
        total_pages = executor.total_pages
        current_page = executor.current_page
        country = executor.country
        name: str = executor.name

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
                            album_position=album_position,
                            album_id=album.id,
                            user_id=user_id,
                            executor_id=executor_id,
                            current_page_executor=current_page,
                            is_global_executor=executor.is_global,
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
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
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
                        callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
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

        # Пагинация исполнителей

        # для избежания выхода за границы
        back_button_page = max(1, current_page - 1)
        forward_button_page = min(total_pages, current_page + 1)

        if pages:  # если исполнителей больше одного
            inline_kb.row(
                InlineKeyboardButton(
                    text="⬅️",
                    callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                        executor_id=executor_id,
                        current_page_executor=back_button_page,
                        user_id=user_id,
                    ).pack(),
                )
            )
            for index, page in enumerate(pages, start=1):
                page_data = f"[{page}]" if page == current_page else page
                inline_kb.add(
                    InlineKeyboardButton(
                        text=f"{page_data}",
                        callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                            executor_id=executor_id,
                            current_page_executor=page,
                            user_id=user_id,
                        ).pack(),
                    )
                )
            inline_kb.add(
                InlineKeyboardButton(
                    text="➡️",
                    callback_data=ScrollingCallbackDataFilters.ExecutorPageLibrary(
                        executor_id=executor_id,
                        current_page_executor=forward_button_page,
                        user_id=user_id,
                    ).pack(),
                )
            )

        # Кнопки исполнителя

        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.ADD_ALBUM,
                callback_data=AddCallbackDataFilters.AddAlbumExecutor(
                    current_page_executor=current_page,
                    executor_id=executor_id,
                    user_id=user_id,
                ).pack(),
            )
        )
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_NAME_EXECUTOR,
                callback_data=UpdateCallbackDataFilters.UserExecutorName(
                    country=country,
                    excecutor_id=executor_id,
                    user_id=user_id,
                    current_page_executor=current_page,
                ).pack(),
            )
        )

        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_PHOTO_EXECUTOR,
                callback_data=UpdateCallbackDataFilters.UserExecutorPhotoFileId(
                    excecutor_id=executor_id,
                    user_id=user_id,
                    current_page_executor=current_page,
                ).pack(),
            )
        )
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_COUNTRY_EXECUTOR,
                callback_data=UpdateCallbackDataFilters.UserExecutorCountry(
                    excecutor_id=executor_id,
                    user_id=user_id,
                    current_page_executor=current_page,
                ).pack(),
            )
        )

        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_EXECUTOR_GENRES,
                callback_data=UpdateCallbackDataFilters.UserExecutorGenres(
                    excecutor_id=executor_id,
                    user_id=user_id,
                    current_page_executor=current_page,
                ).pack(),
            )
        )

        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.DELETE_EXECUTOR,
                callback_data=DeleteCallbackDataFilters.UserExecutor(
                    user_id=user_id,
                    executor_id=executor_id,
                    name=name,
                    current_page_executor=current_page,
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


# общие клавиатуры


def show_album_collections(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    user_id: Optional[int],
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

        song_position: int = max(0, song_position)  # страховка
        songs = songs[song_position : song_position + limit_songs]
        current_page_executor: int = album.current_page_executor
        is_global_executor: bool = album.is_global_executor

        for song in songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data=PlaySongsAlbums(
                        song_id=song.id,
                        album_id=song.album_id,
                    ).pack(),
                )
            )
        buttons = []
        has_prev = song_position > 0
        has_next = song_position + limit_songs < number_of_songs
        if has_prev:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        position=song_position,
                        offset=-limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                    ).pack(),
                )
            )
        if has_next:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        position=song_position,
                        offset=limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                    ).pack(),
                )
            )
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS,
            callback_data=BackExecutorPage(
                album_position=album.album_position,
                current_page=album.current_page_executor,
                user_id=album.user_id,
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


def show_album_user_collections(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    user_id: Optional[int],
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

        song_position: int = max(0, song_position)  # страховка
        songs = songs[song_position : song_position + limit_songs]
        current_page_executor: int = album.current_page_executor
        is_global_executor: bool = album.is_global_executor

        for song in songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{song.position}. {song.title}",
                    callback_data=PlaySongsAlbums(
                        song_id=song.id,
                        album_id=song.album_id,
                    ).pack(),
                )
            )
        buttons = []
        has_prev = song_position > 0
        has_next = song_position + limit_songs < number_of_songs
        if has_prev:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        position=song_position,
                        offset=-limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                    ).pack(),
                )
            )
        if has_next:
            buttons.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        position=song_position,
                        offset=limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                    ).pack(),
                )
            )
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text="Hello World",
            callback_data=BackExecutorPage(
                album_position=album.album_position,
                current_page=album.current_page_executor,
                user_id=album.user_id,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS,
            callback_data=BackExecutorPage(
                album_position=album.album_position,
                current_page=album.current_page_executor,
                user_id=album.user_id,
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


def get_confirmation_delete_executor_button(
    executor_id: int,
    user_id: Optional[int],
    current_page_executor: int,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteExecutor(
                executor_id=executor_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=BackExecutorPage(
                user_id=user_id,
                current_page=current_page_executor,
                album_position=0,
            ).pack(),
        )
    )
    return inline_kb.as_markup()
