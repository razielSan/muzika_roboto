from typing import Optional

from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.global_library.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from infrastructure.aiogram.filters import ScrollingCallbackDataFilters
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.aiogram.messages import LIMIT_ALBUMS
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
        EXECUTOR_DEFAULT_PHOTO_FILE_ID=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
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

    user_id: int = callback_data.user_id
    current_page: int = callback_data.current_page_executor
    position: int = callback_data.position + callback_data.offset

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        EXECUTOR_DEFAULT_PHOTO_FILE_ID=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=user_id,
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
    
    user_id: Optional[int] = callback_data.user_id
    current_page: int = callback_data.current_page_executor

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    
    await ShowExecutorPageService(
        uow=UnitOfWork, logging_data=logging_data, call=call
    ).execute(
        EXECUTOR_DEFAULT_PHOTO_FILE_ID=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=user_id,
        limit_albums=LIMIT_ALBUMS,
        album_position=0,
        current_page=current_page,
        get_information_executor=get_information_executor,
    )
