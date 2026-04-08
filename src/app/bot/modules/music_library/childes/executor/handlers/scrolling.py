from typing import Optional

from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.services.music_library.show_executor_page import (
    ShowExecutorPageCallbackService,
)
from app.bot.services.music_library.show_album_page import ShowAlbumPageCallbackService
from domain.entities.response import LibraryMode, LibraryRole, ExecutorScope
from infrastructure.aiogram.filters import (
    ScrollingCallbackDataFilters,
)
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import LIMIT_ALBUMS, LIMIT_SONGS
from core.logging.api import get_loggers
from core.response.response_data import LoggingData


router: Router = Router(name=__name__)


@router.callback_query(
    StateFilter(None),
    ScrollingCallbackDataFilters.AlbumsExecutorLibrary.filter(),
)
async def scrolling_albums_executor(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.AlbumsExecutorLibrary,
):
    """Пролистывает альбомы исполнителя."""

    current_page: int = callback_data.current_page_executor
    position: int = callback_data.position + callback_data.offset
    user_id: Optional[int] = callback_data.user_id

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    is_admin: bool = callback_data.is_admin
    role: LibraryRole = LibraryRole.ADMIN if is_admin else LibraryRole.USER

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        mode=LibraryMode(
            user_id=user_id,
            role=role,
        ),
        limit_albums=LIMIT_ALBUMS,
        album_position=position,
        current_page=current_page,
        get_information_executor=get_information_executor,
    )


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.ExecutorPageLibrary.filter()
)
async def scrolling_global_executors(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.ExecutorPageLibrary,
):
    """Пролистывает исполнителей."""

    user_id: Optional[int] = callback_data.user_id
    current_page: int = callback_data.current_page_executor
    is_admin: bool = callback_data.is_admin

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    role: LibraryRole = LibraryRole.ADMIN if is_admin else LibraryRole.USER

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        mode=LibraryMode(
            user_id=user_id,
            role=role,
        ),
        limit_albums=LIMIT_ALBUMS,
        album_position=0,
        current_page=current_page,
        get_information_executor=get_information_executor,
    )


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.SongsAlbumLibrary.filter()
)
async def scrolling_songs_album(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SongsAlbumLibrary,
):
    """Пролистывает песни альбома."""

    album_position: int = callback_data.album_position
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    position: int = callback_data.position + callback_data.offset

    mode: LibraryMode = LibraryMode(
        user_id=callback_data.user_id,
        role=LibraryRole.ADMIN if callback_data.is_admin else LibraryRole.USER,
        executor_scope=ExecutorScope.GLOBAL
        if callback_data.is_global_executor
        else ExecutorScope.USER,
    )

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    await ShowAlbumPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        mode=mode,
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=position,
        current_page_executor=current_page_executor,
        album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
        album_position=album_position,
    )
