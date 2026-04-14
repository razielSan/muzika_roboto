from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.executor.settings import settings
from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.services.music_library.show_executor_page import (
    ShowExecutorPageCallbackService,
)
from app.bot.modules.music_library.childes.executor.keyboards.inline import (
    select_library_keyboard,
)
from app.bot.services.music_library.show_album_page import ShowAlbumPageCallbackService
from app.bot.services.music_library.show_song import ShowSongService
from domain.entities.response import LibraryMode, LibraryRole, ExecutorScope
from infrastructure.aiogram.filters import (
    ShowAlbumExecutor,
    PlaySongsAlbums,
    StartUserLibrary,
    StartGlobalLibrary,
)
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.db.db_helper import db_helper
from infrastructure.aiogram.messages import LIMIT_ALBUMS, LIMIT_SONGS, user_messages
from core.logging.api import get_loggers
from core.response.response_data import LoggingData


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def main(call: CallbackQuery):
    """
    Главное обработчик executor.

    Показыает инлайн клавиатуру выбора из библиотек.
    """

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=music_library_settings.MENU_IMAGE_FILE_ID,
            caption=user_messages.USER_PANEL_CAPTION,
        ),
        reply_markup=select_library_keyboard(
            is_admin=False,
        ),
    )


@router.callback_query(StateFilter(None), StartGlobalLibrary.filter())
async def executor_library(
    call: CallbackQuery,
    callback_data: StartGlobalLibrary,
):
    """Показывает первого исполнителя глобальной библиотеки."""

    is_admin: bool = callback_data.is_admin
    role: LibraryRole = LibraryRole.ADMIN if is_admin else LibraryRole.USER

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(session_factory=db_helper.session), logging_data=logging_data, call=call
    ).execute(
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        limit_albums=LIMIT_ALBUMS,
        album_position=0,
        current_page=1,
        get_information_executor=get_information_executor,
        mode=LibraryMode(
            user_id=None,
            role=role,
        ),
    )


@router.callback_query(StateFilter(None), StartUserLibrary.filter())
async def user_library(
    call: CallbackQuery,
    callback_data: StartUserLibrary,
    user,
):
    """Показывает первого исполнителя пользовательской библиотеки."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id: int = user.id

    await ShowExecutorPageCallbackService(
        uow=UnitOfWork(session_factory=db_helper.session),
        logging_data=logging_data,
        call=call,
    ).execute(
        get_information_executor=get_information_executor,
        limit_albums=LIMIT_ALBUMS,
        current_page=1,
        album_position=0,
        mode=LibraryMode(
            user_id=user_id,
            role=LibraryRole.USER,
        ),
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
    )


@router.callback_query(StateFilter(None), ShowAlbumExecutor.filter())
async def show_album_executor(
    call: CallbackQuery,
    callback_data: ShowAlbumExecutor,
):
    """Показывает альбом исполнителя с песнями."""

    executor_id: int = callback_data.executor_id
    current_page_executor = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    mode: LibraryMode = LibraryMode(
        user_id=callback_data.user_id,
        role=LibraryRole.ADMIN if callback_data.is_admin else LibraryRole.USER,
        executor_scope=ExecutorScope.GLOBAL
        if callback_data.is_global_executor
        else ExecutorScope.USER,
    )

    await ShowAlbumPageCallbackService(
        uow=UnitOfWork(session_factory=db_helper.session), logging_data=logging_data, call=call
    ).execute(
        get_information_album=get_information_album,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=LIMIT_SONGS,
        song_position=0,
        current_page_executor=current_page_executor,
        album_position=album_position,
        mode=mode,
        album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
    )


@router.callback_query(StateFilter(None), PlaySongsAlbums.filter())
async def play_songs_album(
    call: CallbackQuery,
    callback_data: PlaySongsAlbums,
    bot: Bot,
):
    """Скидывает песню для прослушивания."""

    album_id = callback_data.album_id
    song_id = callback_data.song_id
    chat_id = call.message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await ShowSongService(
        uow=UnitOfWork(session_factory=db_helper.session),
        logging_data=logging_data,
        call=call,
        bot=bot,
    ).execute(chat_id=chat_id, song_id=song_id, album_id=album_id)
