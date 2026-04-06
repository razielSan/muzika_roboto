from typing import List, Optional

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from domain.entities.response import (
    CollectionSongsResponse,
    ExecutorPageResponse,
    SongResponse,
    AlbumPageResponse,
    Page,
    LibraryMode,
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
    BackAlbumPage,
    BackAdminMenuCallback,
)
from infrastructure.aiogram.filters import ScrollingCallbackDataFilters
from infrastructure.aiogram.keyboards.utils import build_pages


def build_executor_base(
    executor: ExecutorPageResponse,
    album_position: int,
    limit_albums: int,
    is_admin: bool,
):
    """Общие кнопки для страницы исполнителя."""

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    executor_id: int = executor.id
    user_id: Optional[int] = executor.current_user_id
    total_pages: int = executor.total_pages
    current_page: int = executor.current_page

    albums: List[AlbumPageResponse] = executor.albums
    count_albums: int = len(albums)

    album_position: int = max(0, album_position)  # страховка
    albums = albums[album_position : album_position + limit_albums]

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
                        is_admin=is_admin,
                        is_global_executor=executor.is_global,
                    ).pack(),
                )
            )

        page = Page(
            items=[],
            position=album_position,
            total=count_albums,
            limit=limit_albums,
        )
        if page.has_prev:
            page.items.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
                        executor_id=executor_id,
                        user_id=user_id,
                        current_page_executor=current_page,
                        position=album_position,
                        offset=-limit_albums,
                        is_admin=is_admin,
                    ).pack(),
                )
            )
        if page.has_next:
            page.items.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.AlbumsExecutorLibrary(
                        executor_id=executor_id,
                        user_id=user_id,
                        current_page_executor=current_page,
                        position=album_position,
                        offset=limit_albums,
                        is_admin=is_admin,
                    ).pack(),
                )
            )
        inline_kb.row(*page.items)
    pages: List[int] = build_pages(current=current_page, total=total_pages)

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
                    is_admin=is_admin,
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
                        is_admin=is_admin,
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
                    is_admin=is_admin,
                ).pack(),
            )
        )

    return inline_kb


def show_executor_user(
    executor: ExecutorPageResponse,
    album_position: int,
    limit_albums: int,
    is_admin: bool,
):
    inline_kb = build_executor_base(
        executor=executor,
        album_position=album_position,
        limit_albums=limit_albums,
        is_admin=is_admin,
    )

    executor_id: int = executor.id
    user_id: Optional[int] = executor.current_user_id
    current_page: int = executor.current_page
    country: str = executor.country

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_ALBUM,
            callback_data=AddCallbackDataFilters.AddAlbumExecutor(
                current_page_executor=current_page,
                executor_id=executor_id,
                user_id=user_id,
                is_admin=is_admin,
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
                album_position=album_position,
                is_admin=is_admin,
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
                album_position=album_position,
                is_admin=is_admin,
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
                album_position=album_position,
                is_admin=is_admin,
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
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_EXECUTOR,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteExecutor(
                user_id=user_id,
                executor_id=executor_id,
                current_page_executor=current_page,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )
    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()


def show_executor_global(
    limit_albums: int,
    album_position: int,
    executor: ExecutorPageResponse = None,
    is_sync_executor=True,
    is_admin=False,
):
    inline_kb = build_executor_base(
        executor=executor,
        album_position=album_position,
        limit_albums=limit_albums,
        is_admin=is_admin,
    )
    executor_id: int = executor.id

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

    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()


def build_executor_keyboards(
    mode: LibraryMode,
    executor: ExecutorPageResponse,
    album_position: int,
    limit_albums: int,
):
    if mode.is_admin:
        return show_executor_user(
            limit_albums=limit_albums,
            executor=executor,
            is_admin=True,
            album_position=album_position,
        )

    if mode.global_library:
        return show_executor_global(
            limit_albums=limit_albums,
            album_position=album_position,
            executor=executor,
            is_admin=False,
            is_sync_executor=True,
        )
    if mode.user_library:
        if executor.is_global:
            return show_executor_global(
                limit_albums=limit_albums,
                album_position=album_position,
                executor=executor,
                is_admin=False,
                is_sync_executor=False,
            )
        else:
            return show_executor_user(
                limit_albums=limit_albums,
                executor=executor,
                is_admin=False,
                album_position=album_position,
            )


def build_album_base(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    is_admin: bool,
    user_id: Optional[int],
):
    """Общие кнопки для страницы альбома."""

    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()

    executor_id: int = album.executor_id
    album_id: int = album.id
    current_page_executor: int = album.current_page_executor
    is_global_executor: bool = album.is_global_executor

    if not songs:  # в альбоме нет песен
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.NOT_FOUND_SONGS,
                callback_data="NOT_FOUND_SONGS",
            )
        )

    else:
        songs: List[SongResponse] = album.songs
        number_of_songs: int = len(songs)
        song_position: int = max(0, song_position)  # страховка
        songs = songs[song_position : song_position + limit_songs]

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

        page = Page(
            items=[],
            position=song_position,
            total=number_of_songs,
            limit=limit_songs,
        )
        if page.has_prev:
            page.items.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.BACK_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        album_position=album.album_position,
                        position=song_position,
                        offset=-limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                        is_admin=is_admin,
                    ).pack(),
                )
            )
        if page.has_next:
            page.items.append(
                InlineKeyboardButton(
                    text=KeyboardResponse.FORWARD_BUTTON,
                    callback_data=ScrollingCallbackDataFilters.SongsAlbumLibrary(
                        album_position=album.album_position,
                        position=song_position,
                        offset=limit_songs,
                        executor_id=executor_id,
                        current_page_executor=current_page_executor,
                        album_id=album_id,
                        user_id=user_id,
                        is_global_executor=is_global_executor,
                        is_admin=is_admin,
                    ).pack(),
                )
            )
        inline_kb.row(*page.items)

    return inline_kb


def show_album_user(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    user_id: Optional[int],
    is_admin: bool,
):
    inline_kb = build_album_base(
        songs=songs,
        album=album,
        song_position=song_position,
        limit_songs=limit_songs,
        user_id=user_id,
        is_admin=is_admin,
    )
    album_position: int = album.album_position
    executor_id: int = album.executor_id
    album_id: int = album.id
    current_page_executor: int = album.current_page_executor
    is_global_executor: bool = album.is_global_executor

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.AddSongsAlbum(
                executor_id=executor_id,
                album_id=album_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )

    if songs:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.UPDATE_TITLE_SONG,
                callback_data=UpdateCallbackDataFilters.SongTitle(
                    executor_id=executor_id,
                    album_id=album_id,
                    user_id=user_id,
                    current_page_executor=current_page_executor,
                    is_global_executor=is_global_executor,
                    album_position=album_position,
                    is_admin=is_admin,
                ).pack(),
            )
        )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_PHOTO_ALBUM,
            callback_data=UpdateCallbackDataFilters.AlbumPhoto(
                executor_id=executor_id,
                album_id=album_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_TITLE_ALBUM,
            callback_data=UpdateCallbackDataFilters.AlbumTitle(
                executor_id=executor_id,
                album_id=album_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.UPDATE_YEAR_ALBUM,
            callback_data=UpdateCallbackDataFilters.AlbumYear(
                executor_id=executor_id,
                album_id=album_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )
    if songs:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.DELETE_SONGS,
                callback_data=DeleteCallbackDataFilters.SongsAlbum(
                    executor_id=executor_id,
                    user_id=user_id,
                    current_page_executor=current_page_executor,
                    is_global_executor=is_global_executor,
                    album_id=album_id,
                    album_position=album_position,
                    is_admin=is_admin,
                ).pack(),
            )
        )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.DELETE_ALBUM,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteAlbum(
                executor_id=executor_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                album_id=album_id,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS,
            callback_data=BackExecutorPage(
                album_position=album_position,
                current_page=current_page_executor,
                user_id=user_id,
                is_admin=is_admin,
            ).pack(),
        )
    )
    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()


def show_album_global(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    user_id: Optional[int],
    is_admin: bool,
):
    inline_kb = build_album_base(
        songs=songs,
        album=album,
        song_position=song_position,
        limit_songs=limit_songs,
        user_id=user_id,
        is_admin=is_admin,
    )

    album_position: int = album.album_position
    current_page_executor: int = album.current_page_executor

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.BACK_TO_ALBUMS,
            callback_data=BackExecutorPage(
                album_position=album_position,
                current_page=current_page_executor,
                user_id=user_id,
                is_admin=is_admin,
            ).pack(),
        )
    )
    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_USER_PANEL,
                callback_data=BackMenuUserPanel().pack(),
            )
        )

    return inline_kb.as_markup()


def build_album_keyboards(
    songs: List[SongResponse],
    album: AlbumPageResponse,
    song_position: int,
    limit_songs: int,
    user_id: Optional[int],
    is_admin: bool,
    is_global_executor: bool,
):
    if is_admin:
        return show_album_user(
            songs=songs,
            album=album,
            song_position=song_position,
            limit_songs=limit_songs,
            user_id=None,
            is_admin=is_admin,
        )
    if is_global_executor:  # если глобальная библиотека
        return show_album_global(
            songs=songs,
            album=album,
            song_position=song_position,
            limit_songs=limit_songs,
            user_id=user_id,
            is_admin=is_admin,
        )
    if not is_global_executor:  # если пользовательская
        return show_album_user(
            songs=songs,
            album=album,
            song_position=song_position,
            limit_songs=limit_songs,
            user_id=user_id,
            is_admin=is_admin,
        )


### инлайн клавиатуры для сборника песен


def get_buttons_for_song_collection_empty_user(
    is_admin=False,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.ADD_SONGS,
            callback_data=AddCallbackDataFilters.SongCollectionSongs().pack(),
        )
    )
    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
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
    is_admin: bool = False,
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
    if is_admin:
        inline_kb.row(
            InlineKeyboardButton(
                text=KeyboardResponse.BACK_TO_THE_ADMIN_PANEL,
                callback_data=BackAdminMenuCallback().pack(),
            )
        )
    else:
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
    is_admin: bool = False,
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


def get_confirmation_delete_song_button(
    is_admin: bool = False,
):
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


#### клавиатуры для удаления


def get_menu_album_songs_delete(
    user_id: Optional[int],
    album_id: int,
    executor_id: int,
    album_position: int,
    is_global_executor: bool,
    current_page_executor: int,
    songs: List[SongResponse],
    song_position: int = 0,
    len_list_songs=0,
    limit_songs=5,
    is_admin: bool = False,
    delete_songs: set = None,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for song in songs:
        if not delete_songs:
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"☑ {song.position}. {song.title}",
                    callback_data=DeleteCallbackDataFilters.ButtonsDeleteSongAlbum(
                        song_id=song.id,
                        position=song_position,
                    ).pack(),
                )
            )
        else:
            delete_img = "✅" if song.id in delete_songs else "☑ "
            inline_kb.row(
                InlineKeyboardButton(
                    text=f"{delete_img} {song.position}. {song.title}",
                    callback_data=DeleteCallbackDataFilters.ButtonsDeleteSongAlbum(
                        song_id=song.id,
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
                callback_data=ScrollingCallbackDataFilters.DeleteMenuSongAlbum(
                    position=song_position, offset=-limit_songs
                ).pack(),
            )
        )

    if has_next:
        buttons.append(
            InlineKeyboardButton(
                text=KeyboardResponse.FORWARD_BUTTON.value,
                callback_data=ScrollingCallbackDataFilters.DeleteMenuSongAlbum(
                    position=song_position, offset=limit_songs
                ).pack(),
            )
        )

    if buttons:
        inline_kb.row(*buttons)

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CONFIRM_DELETE.value,
            callback_data=DeleteCallbackDataFilters.ConfirmDeleteSongAlbum(
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.CANCEL_DELETE.value,
            callback_data=BackAlbumPage(
                user_id=user_id,
                album_id=album_id,
                executor_id=executor_id,
                album_position=album_position,
                current_page_executor=current_page_executor,
                is_global_executor=is_global_executor,
                is_admin=is_admin,
            ).pack(),
        )
    )

    return inline_kb.as_markup()


def get_confirmation_delete_executor_button(
    executor_id: int,
    user_id: Optional[int],
    current_page_executor: int,
    album_position: int,
    is_admin: bool,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=DeleteCallbackDataFilters.CompleteDeleteExecutor(
                executor_id=executor_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                is_admin=is_admin,
            ).pack(),
        )
    )
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=BackExecutorPage(
                user_id=user_id,
                current_page=current_page_executor,
                album_position=album_position,
                is_admin=is_admin,
            ).pack(),
        )
    )
    return inline_kb.as_markup()


def get_confirmation_delete_album_buttons(
    executor_id: int,
    user_id: Optional[int],
    current_page_executor: int,
    is_global_executor: bool,
    album_id: int,
    album_position: int,
    is_admin: bool,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=DeleteCallbackDataFilters.CompleteDeleteAlbum(
                executor_id=executor_id,
                user_id=user_id,
                current_page_executor=current_page_executor,
                album_id=album_id,
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=BackAlbumPage(
                user_id=user_id,
                current_page_executor=current_page_executor,
                album_position=album_position,
                is_global_executor=is_global_executor,
                album_id=album_id,
                executor_id=executor_id,
                is_admin=is_admin,
            ).pack(),
        )
    )
    return inline_kb.as_markup()


def get_confirmation_delete_album_songs_button(
    executor_id: int,
    user_id: Optional[int],
    current_page_executor: int,
    is_global_executor: bool,
    album_id: int,
    album_position: int,
    is_admin: bool = False,
):
    inline_kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.YES.value,
            callback_data=DeleteCallbackDataFilters.CompleteDeleteSongAlbum(
                is_admin=is_admin,
            ).pack(),
        )
    )

    inline_kb.row(
        InlineKeyboardButton(
            text=KeyboardResponse.NO.value,
            callback_data=BackAlbumPage(
                user_id=user_id,
                current_page_executor=current_page_executor,
                album_position=album_position,
                is_global_executor=is_global_executor,
                album_id=album_id,
                executor_id=executor_id,
                is_admin=is_admin,
            ).pack(),
        )
    )
    return inline_kb.as_markup()
