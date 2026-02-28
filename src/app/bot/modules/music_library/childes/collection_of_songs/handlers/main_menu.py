from typing import List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from app.bot.modules.music_library.services.collection_songs import (
    callback_show_user_collection,
)
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from domain.entities.response import (
    UserCollectionSongsResponse,
    CollectionSongsResponse,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.filters import ScrollingCallbackDataFilters
from infrastructure.aiogram.keyboards.inline import (
    get_buttons_for_song_collection_empty_user,
    get_buttons_for_song_collection_user,
)
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_COLLECTION_SONGS,
    resolve_error_message,
)
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def main_menu(call: CallbackQuery, bot: Bot):
    """Возвращает инлайн меню модуля music_library."""
    
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    telegram: int = call.message.chat.id

    result: Result = await GetUserCollectionSongs(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    if result.ok and not result.empty:
        await callback_show_user_collection(
            user_response=result.data,
            call=call,
            start_collection_songs=0,
            limit_collection_songs=LIMIT_COLLECTION_SONGS,
            photo_file_id=music_library_settings.COLLECTION_SONGS_PHOTO_FILE_ID,
            caption=user_messages.MY_COLLECTION_OF_SONGS,
        )

    if result.ok and result.empty:  # если пустой сборник
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=music_library_settings.COLLECTION_SONGS_PHOTO_FILE_ID,
                caption=f"{user_messages.THERE_ARE_NO_SONGS}",
            ),
            reply_markup=get_buttons_for_song_collection_empty_user(),
        )

    if not result.ok:
        error_message: str = resolve_error_message(error_code=result.error.code)
        await call.message.answer(text=error_message)


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.SongCollectionSong.filter()
)
async def scrolling_song_collection(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SongCollectionSong,
):

    telegram: int = call.message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    position: int = callback_data.position + callback_data.offset
    result: Result = await GetUserCollectionSongs(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    if result.ok and not result.empty:
        user_response: UserCollectionSongsResponse = result.data
        collection_songs = user_response.collection_songs
        len_collection_songs: int = len(collection_songs)

        collection_songs: List[CollectionSongsResponse] = collection_songs[
            position : position + LIMIT_COLLECTION_SONGS
        ]
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=music_library_settings.COLLECTION_SONGS_PHOTO_FILE_ID,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
            ),
            reply_markup=get_buttons_for_song_collection_user(
                colellection_songs=collection_songs,
                len_collection_songs=len_collection_songs,
                limit_songs=LIMIT_COLLECTION_SONGS,
                song_position=position,
            ),
        )
    if not result.ok:
        error_message: str = resolve_error_message(error_code=result.error.code)

        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MAIN_MENU,
            message=error_message,
        )
