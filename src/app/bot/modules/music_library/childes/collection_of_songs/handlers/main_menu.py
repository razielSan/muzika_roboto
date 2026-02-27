from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from application.use_cases.db.get_user_collection_song import GetUserCollectionSong
from app.bot.modules.music_library.settings import settings as music_library_settings
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from infrastructure.aiogram.keyboards.inline import (
    get_buttons_for_song_collection_empty_user,
    get_buttons_for_song_collection_user,
)
from domain.errors.error_code import NotFoundCode, ErorrCode
from infrastructure.aiogram.messages import (
    ERRORS,
    NOT_FOUND,
    user_messages,
    LIMIT_COLLECTION_SONG,
)
from infrastructure.aiogram.filters import ScrollingCallbackDataFilters
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from app.bot.modules.music_library.utils.music_library import (
    callback_show_user_collection,
)

router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def main_menu(call: CallbackQuery, bot: Bot):
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    telegram = call.message.chat.id

    result = await GetUserCollectionSong(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    if result.ok and not result.empty:
        await callback_show_user_collection(
            user_response=result.data,
            call=call,
            start_collection_song=0,
            limit_collection_song=LIMIT_COLLECTION_SONG,
            photo_file_id=music_library_settings.COLLECTION_SONG_PHOTO_FILE_ID,
            caption=user_messages.MY_COLLECTION_OF_SONGS,
        )

    if result.ok and result.empty:  # если пустой сборник
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=music_library_settings.COLLECTION_SONG_PHOTO_FILE_ID,
                caption=f"{user_messages.THERE_ARE_NO_SONGS}",
            ),
            reply_markup=get_buttons_for_song_collection_empty_user(),
        )

    if not result.ok:
        if (
            result.error.code == NotFoundCode.USER_NOT_FOUND.name
        ):  # если пользователь не найден
            await call.message.answer(NOT_FOUND[result.error.code])

        if result.error.code == ErorrCode.UNKNOWN_ERROR.name:
            await call.message.answer(ERRORS[result.error.code])
        return


@router.callback_query(
    StateFilter(None), ScrollingCallbackDataFilters.CollectionSong.filter()
)
async def scrolling_song_collection(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.CollectionSong,
    bot: Bot,
):

    telegram: int = call.message.chat.id
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    position: int = callback_data.position + callback_data.offset
    result = await GetUserCollectionSong(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    if result.ok and not result.empty:
        user_response = result.data
        collection_songs = user_response.collection_songs
        len_collection_songs = len(collection_songs)

        collection_songs = collection_songs[position : position + LIMIT_COLLECTION_SONG]
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=music_library_settings.COLLECTION_SONG_PHOTO_FILE_ID,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
            ),
            reply_markup=get_buttons_for_song_collection_user(
                colellection_songs=collection_songs,
                len_collection_songs=len_collection_songs,
                limit_songs=LIMIT_COLLECTION_SONG,
                song_position=position,
            ),
        )
    if not result.ok:
        error_message = None
        if result.error.code == ErorrCode.UNKNOWN_ERROR.name:
            error_message = ERRORS[result.error.code]

        if result.error.code == NotFoundCode.USER_NOT_FOUND.name:
            error_message = NOT_FOUND[result.error.code]

        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MAIN_MENU,
            message=error_message,
        )
