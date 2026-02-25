from typing import List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.admin.childes.base_music.settings import settings
from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.settings import settings as bot_settings
from app.bot.keyboards.inlinle import (
    show_one_album_songs_with_base_executor,
    show_base_executor_collections,
)
from app.bot.modules.admin.childes.base_music.services.base_music import (
    base_music_service,
)
from app.bot.view_model import SongResponse
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.utils.editing import get_info_album, get_info_executor
from app.bot.filters.admin_filters import (
    AdminBackExecutorCallback,
    AdminMusicCallback,
    AdminPlaySongCallback,
    AdminScrollingSongsCallback,
    AdminScrollingExecutorsCallback,
    AdminScrollingAlbumsCallback,
)
from app.bot.view_model import ExecutorResponse, AlbumResponse
from infrastructure.aiogram.legacy_response import ServerDatabaseResponse
from infrastructure.aiogram.response import LIMIT_SONGS, LIMIT_ALBUMS
from app.bot.modules.admin.utils.admin import callback_update_admin_panel_media_photo
from core.response.response_data import Result


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def base_music(call: CallbackQuery) -> None:
    """Возвращает первого исполнителя из базового музыкального хранилища."""

    result_executor: Result = await base_music_service.show_executor(
        get_info_executor=get_info_executor,
    )
    if result_executor.ok:
        executor: ExecutorResponse = result_executor.data.executor
        albums_list: List[AlbumResponse] = result_executor.data.albums
        len_list_albums: int = len(albums_list)
        if albums_list:
            albums_list = albums_list[0:LIMIT_ALBUMS]
        total_pages: int = result_executor.data.total_pages
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=executor.photo_file_id,
                caption=executor.info_executor,
            ),
            reply_markup=show_base_executor_collections(
                list_albums=albums_list,
                executor_id=executor.executor_id,
                count_pages_executor=total_pages,
                current_page_executor=1,
                limit_albums=LIMIT_ALBUMS,
                album_position=0,
                len_list_albums=len_list_albums,
            ),
        )
    else:
        try:  # При повторном нажатии кнопки когда нет исполнителей
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption=result_executor.error.message,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )
        except Exception:
            pass


@router.callback_query(StateFilter(None), AdminMusicCallback.filter())
async def show_songs_with_album(
    call: CallbackQuery,
    callback_data: AdminMusicCallback,
) -> None:
    """Возвращает альбом со списком песен для исполнителя."""

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    result: Result = await base_music_service.show_songs_with_album(
        executor_id=executor_id,
        album_id=album_id,
        get_info_album=get_info_album,
    )
    if result.ok and not result.empty:  # если есть песни в альбоме
        songs: List[SongResponse] = result.data
        len_list_songs: int = len(songs)

        songs = songs[0:LIMIT_SONGS]  # ограничиваем список песен на страгице
        song: SongResponse = songs[0]
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=song.album_photo_file_id,
                caption=song.info_album,
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=songs,
                executor_id=executor_id,
                album_id=album_id,
                len_list_songs=len_list_songs,
                limit_songs=LIMIT_SONGS,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ),
        )
    if result.ok and result.empty:  # если нет песен в альбоме
        song: SongResponse = result.data

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=song.album_photo_file_id,
                caption=f"{song.info_album}\n\n{ServerDatabaseResponse.NOT_FOUND_SONGS.value}",
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=[],
                executor_id=executor_id,
                album_id=album_id,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ),
        )

    if not result.ok:  # если произошла ошибка
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(StateFilter(None), AdminScrollingExecutorsCallback.filter())
async def scrolling_base_executors(
    call: CallbackQuery,
    callback_data: AdminScrollingExecutorsCallback,
    bot: Bot,
) -> None:
    """Пролистывает исполнителей."""

    current_page_executor: int = callback_data.current_page

    result_executor: Result = await base_music_service.show_executor(
        get_info_executor=get_info_executor,
        page_executor=current_page_executor,
    )

    if result_executor.ok:
        executor: ExecutorResponse = result_executor.data.executor
        albums_list: List[AlbumResponse] = result_executor.data.albums
        len_list_albums: int = len(albums_list)
        if albums_list:
            albums_list = albums_list[0:LIMIT_ALBUMS]

        total_pages: int = result_executor.data.total_pages

        try:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=executor.photo_file_id,
                    caption=executor.info_executor,
                ),
                reply_markup=show_base_executor_collections(
                    list_albums=albums_list,
                    executor_id=executor.executor_id,
                    count_pages_executor=total_pages,
                    current_page_executor=current_page_executor,
                    limit_albums=LIMIT_ALBUMS,
                    album_position=0,
                    len_list_albums=len_list_albums,
                ),
            )

        except Exception:
            await bot.answer_callback_query(
                call.id,
                text="Исполнитель уже загружен",
                show_alert=True,
            )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result_executor.error.message
        )


@router.callback_query(StateFilter(None), AdminScrollingAlbumsCallback.filter())
async def scrolling_base_albums(
    call: CallbackQuery,
    callback_data: AdminScrollingAlbumsCallback,
    bot: Bot,
) -> None:
    """Пролистывает альбомы."""
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.position + callback_data.offset

    result_executor: Result = await base_music_service.show_executor(
        get_info_executor=get_info_executor,
        page_executor=current_page_executor,
    )
    if result_executor.ok:
        executor: ExecutorResponse = result_executor.data.executor
        albums_list: List[AlbumResponse] = result_executor.data.albums
        len_list_albums: int = len(albums_list)

        albums_list = albums_list[album_position : album_position + LIMIT_ALBUMS]
        total_pages: int = result_executor.data.total_pages

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=executor.photo_file_id,
                caption=executor.info_executor,
            ),
            reply_markup=show_base_executor_collections(
                list_albums=albums_list,
                executor_id=executor.executor_id,
                count_pages_executor=total_pages,
                current_page_executor=current_page_executor,
                limit_albums=LIMIT_ALBUMS,
                album_position=album_position,
                len_list_albums=len_list_albums,
            ),
        )
        return


@router.callback_query(StateFilter(None), AdminScrollingSongsCallback.filter())
async def scrolling_songs_with_album(
    call: CallbackQuery,
    callback_data: AdminScrollingSongsCallback,
) -> None:
    """Пролистывает песни из альбома."""

    current_position: int = max(0, callback_data.position + callback_data.offset)  # на
    # случай ухода в минус
    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id
    current_page_executor: int = callback_data.current_page_executor
    count_pages_executor: int = callback_data.count_pages_executor

    result: Result = await base_music_service.show_songs_with_album(
        executor_id=executor_id,
        album_id=album_id,
        get_info_album=get_info_album,
    )
    if result.ok:
        songs: List[SongResponse] = result.data

        len_list_songs: int = len(songs)

        songs = songs[current_position : current_position + LIMIT_SONGS]
        song: SongResponse = songs[0]
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=song.album_photo_file_id,
                caption=song.info_album,
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=songs,
                executor_id=executor_id,
                album_id=album_id,
                len_list_songs=len_list_songs,
                song_position=current_position,
                limit_songs=LIMIT_SONGS,
                current_page_executor=current_page_executor,
                count_pages_executor=count_pages_executor,
            ),
        )

    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
                caption=result.error.message,
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=[],
                executor_id=executor_id,
                album_id=album_id,
            ),
        )


@router.callback_query(StateFilter(None), AdminBackExecutorCallback.filter())
async def back_to_executor(
    call: CallbackQuery,
    callback_data: AdminBackExecutorCallback,
) -> None:
    """Возвращает назад к исполнителю, при нажатии кнопки."""

    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor

    result_executor: Result = await base_music_service.back_executor(
        get_info_executor=get_info_executor,
        current_page_executor=current_page_executor,
    )

    if result_executor.ok:
        albums_list: List[AlbumResponse] = result_executor.data
        len_list_albums: int = len(albums_list)

        if albums_list:
            albums_list = albums_list[0:LIMIT_ALBUMS]
        album: AlbumResponse = albums_list[0]

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=album.executor_photo_file_id,
                caption=album.info_executor,
            ),
            reply_markup=show_base_executor_collections(
                list_albums=albums_list,
                executor_id=executor_id,
                count_pages_executor=album.count_executors,
                current_page_executor=current_page_executor,
                album_position=0,
                limit_albums=LIMIT_ALBUMS,
                len_list_albums=len_list_albums,
            ),
        )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result_executor.error.message
        )


@router.callback_query(StateFilter(None), AdminPlaySongCallback.filter())
async def play_song(
    call: CallbackQuery,
    callback_data: AdminPlaySongCallback,
    bot: Bot,
) -> None:
    """Скидывает песню для прослушивания."""

    position: int = callback_data.position
    album_id: int = callback_data.album_id

    result: Result = await base_music_service.play_song(
        album_id=album_id,
        position=position,
    )

    if result.ok:
        song: SongResponse = result.data
        await bot.send_audio(
            chat_id=call.message.chat.id,
            audio=song.file_id,
            caption=f"{song.position}. {song.title}",
        )
    else:
        await call.message.answer(
            text=f"{result.error.message}\n\nПопробуйте,снова,запустить песню"
        )
