from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.global_library.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from app.bot.services.music_library.show_album_page import ShowAlbumPageService
from infrastructure.aiogram.filters import (
    ScrollingCallbackDataFilters,
    ShowAlbumExecutor,
)
from application.use_cases.db.music_library.get_album_with_songs import (
    GetAlbumWithSongs,
)
from domain.entities.response import AlbumPageResponse, SongResponse
from infrastructure.aiogram.keyboards.inline import show_album_global_collections
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import LIMIT_ALBUMS, LIMIT_SONGS
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from core.response.response_data import LoggingData


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def global_libaray(call: CallbackQuery):
    """
    Главное обработчик global_library.

    Показыает первого исполнтиеля библиотеки.
    """
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=None,
        limit_albums=LIMIT_ALBUMS,
        album_position=0,
        current_page=1,
        get_information_executor=get_information_executor,
    )


@router.callback_query(
    StateFilter(None),
    ScrollingCallbackDataFilters.AlbumsExecutorGlobalLibrary.filter(),
)
async def scrolling_albums_executor(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.AlbumsExecutorGlobalLibrary,
):
    """Пролистывает альбомы исполнителя."""

    current_page: int = callback_data.current_page_executor
    position: int = callback_data.position + callback_data.offset

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=None,
        limit_albums=LIMIT_ALBUMS,
        album_position=position,
        current_page=current_page,
        get_information_executor=get_information_executor,
    )


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.ExecutorPageGlobalLibrary.filter()
)
async def scrolling_global_executors(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.ExecutorPageGlobalLibrary,
):
    """Пролистывает исполнителей."""

    current_page: int = callback_data.current_page_executor

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=None,
        limit_albums=LIMIT_ALBUMS,
        album_position=0,
        current_page=current_page,
        get_information_executor=get_information_executor,
    )


@router.callback_query(StateFilter(None), ShowAlbumExecutor.filter())
async def show_album_executor(
    call: CallbackQuery,
    callback_data: ShowAlbumExecutor,
):
    """Показывает альбом исполнителя с песнями."""

    executor_id = callback_data.executor_id
    current_page_executor = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowAlbumPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        user_id=None,
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=0,
        current_page_executor=current_page_executor,
    )


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.SongsAlbumGlobalLibrary.filter()
)
async def scrolling_songs_album(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SongsAlbumGlobalLibrary,
):
    """Пролистывает песни альбома."""

    executor_id = callback_data.executor_id
    current_page_executor = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    position = callback_data.position + callback_data.offset

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowAlbumPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        user_id=None,
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=position,
        current_page_executor=current_page_executor,
    )
