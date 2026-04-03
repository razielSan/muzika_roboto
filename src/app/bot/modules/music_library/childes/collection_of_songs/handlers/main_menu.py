from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from app.bot.modules.music_library.services.collection_songs import (
    callback_show_user_collection,
)
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from application.use_cases.db.collection_songs.get_song import GetSongCollectionSongs
from domain.entities.response import (
    UserCollectionSongsResponse,
)
from domain.entities.response import CollectionSongsResponse
from domain.entities.db.models.user import User
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.filters import (
    ScrollingCallbackDataFilters,
    PlaySongsCollectionSongs,
)
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_COLLECTION_SONGS,
    resolve_message,
)
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def main_menu(
    call: CallbackQuery,
    bot: Bot,
    user: User,
):
    """Возвращает инлайн меню модуля music_library."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result: Result = await GetUserCollectionSongs(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(user=user)

    if result.ok:
        user_response: UserCollectionSongsResponse = result.data

        await callback_show_user_collection(
            user_response=user_response,
            call=call,
            start_collection_songs=0,
            limit_collection_songs=LIMIT_COLLECTION_SONGS,
            caption=user_messages.MY_COLLECTION_OF_SONGS,
            is_admin=False,
        )

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await call.message.answer(text=error_message)


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.SongCollectionSongs.filter()
)
async def scrolling_song_collection(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SongCollectionSongs,
    user: User,
):
    """Пролистывает песни из сборника."""
    
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    position: int = callback_data.position + callback_data.offset
    result: Result = await GetUserCollectionSongs(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(user=user)

    if result.ok:

        user_response: UserCollectionSongsResponse = result.data

        await callback_show_user_collection(
            user_response=user_response,
            call=call,
            start_collection_songs=position,
            limit_collection_songs=LIMIT_COLLECTION_SONGS,
            caption=user_messages.MY_COLLECTION_OF_SONGS,
        )

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)

        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MY_MUSIC_COLLECTION,
            message=error_message,
        )


@router.callback_query(StateFilter(None), PlaySongsCollectionSongs.filter())
async def play_songs(
    call: CallbackQuery,
    callback_data: PlaySongsCollectionSongs,
    bot: Bot,
    user: User,
):
    """Скидывает песню."""

    song_id: int = callback_data.song_id
    chat_id: int = call.message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_get_song: Result = await GetSongCollectionSongs(
        uow=UnitOfWork(),
        logging_data=logging_data,
    ).execute(user_id=user.id, song_id=song_id)
    if result_get_song.ok:
        song: CollectionSongsResponse = result_get_song.data
        await bot.send_audio(
            chat_id=chat_id,
            audio=song.file_id,
            caption=f"{song.position}. {song.title}",
        )
    if not result_get_song.ok:
        msg_error: str = resolve_message(code=result_get_song.error.code)
        await call.message.answer(text=msg_error)
