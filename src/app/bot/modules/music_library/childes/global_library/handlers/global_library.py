from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.global_library.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.services.music_library.show_executor_page import (
    ShowExecutorPageCallbackService,
)
from app.bot.services.music_library.show_song import ShowSongService
from app.bot.services.music_library.show_album_page import ShowAlbumPageService
from application.use_cases.db.music_library.sync_executor import SyncExecutorLibrary
from infrastructure.aiogram.filters import (
    ScrollingCallbackDataFilters,
    ShowAlbumExecutor,
    PlaySongsAlbums,
    SyncExecutor,
)
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import LIMIT_ALBUMS, LIMIT_SONGS, resolve_message
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

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
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
    ScrollingCallbackDataFilters.AlbumsExecutorLibrary.filter(),
)
async def scrolling_albums_executor(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.AlbumsExecutorLibrary,
):
    """Пролистывает альбомы исполнителя."""

    current_page: int = callback_data.current_page_executor
    position: int = callback_data.position + callback_data.offset
    user_id = callback_data.user_id

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=user_id,
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

    user_id = callback_data.user_id
    current_page: int = callback_data.current_page_executor

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        user_id=user_id,
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

    user_id = callback_data.user_id
    executor_id = callback_data.executor_id
    current_page_executor = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowAlbumPageService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        user_id=user_id,
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=0,
        current_page_executor=current_page_executor,
        album_position=album_position,
        is_global_executor=is_global_executor
    )


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.SongsAlbumLibrary.filter()
)
async def scrolling_songs_album(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SongsAlbumLibrary,
):
    """Пролистывает песни альбома."""

    executor_id = callback_data.executor_id
    current_page_executor = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    position = callback_data.position + callback_data.offset
    user_id = callback_data.user_id
    is_global_executor: bool = callback_data.is_global_executor

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowAlbumPageService(
        uow=UnitOfWork(), logging_data=logging_data, call=call
    ).execute(
        user_id=user_id,
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=position,
        current_page_executor=current_page_executor,
        is_global_executor=is_global_executor
    )


@router.callback_query(StateFilter(None), PlaySongsAlbums.filter())
async def play_songs_album(
    call: CallbackQuery,
    callback_data: PlaySongsAlbums,
    bot: Bot,
):

    album_id = callback_data.album_id
    song_id = callback_data.song_id
    chat_id = call.message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowSongService(
        uow=UnitOfWork(),
        logging_data=logging_data,
        call=call,
        bot=bot,
    ).execute(chat_id=chat_id, song_id=song_id, album_id=album_id)


@router.callback_query(StateFilter(None), SyncExecutor.filter())
async def sync_executor(
    call: CallbackQuery,
    callback_data: SyncExecutor,
    user,
):
    user_id = user.id
    executor_id = callback_data.executor_id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_sync = await SyncExecutorLibrary(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, user_id=user_id)

    if result_sync.ok:
        success_message = resolve_message(code=result_sync.code)
        await call.answer(text=success_message)

    if not result_sync.ok:
        error_message = resolve_message(code=result_sync.error.code)
        await call.answer(text=error_message)
