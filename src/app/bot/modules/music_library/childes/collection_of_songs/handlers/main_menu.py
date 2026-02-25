from aiogram import Router, F
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from application.use_cases.db.get_user_collection_song import GetUserCollectionSong
from app.bot.modules.music_library.settings import settings as music_library_settings
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from core.response.messages import telegram_emoji
from infrastructure.aiogram.keyboards.inline import (
    get_buttons_for_song_collection_empty_user,
)


router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def main_menu(call: CallbackQuery):
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    telegram = call.message.chat.id

    result = await GetUserCollectionSong(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    if result.ok and result.empty:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=music_library_settings.COLLECTION_SONG_PHOTO_FILE_ID,
                caption=f"{telegram_emoji.yellow_triangle_with_exclamation_mark} "
                "У вас нет песен в сборнике",
            ),
            reply_markup=get_buttons_for_song_collection_empty_user(),
        )
