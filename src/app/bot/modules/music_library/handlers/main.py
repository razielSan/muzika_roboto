from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.modules.music_library.settings import settings
from app.bot.modules.music_library.services.collection_songs import show_user_collection
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from app.bot.utils.delete import delete_previous_message
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from infrastructure.aiogram.messages import user_messages
from infrastructure.aiogram.messages import LIMIT_COLLECTION_SONGS
from infrastructure.aiogram.keyboards.inline import (
    get_buttons_for_song_collection_empty_user,
)
from infrastructure.db.uow import UnitOfWork
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers


router: Router = Router(name=settings.SERVICE_NAME)


@router.message(StateFilter(None), F.text == f"/{settings.SERVICE_NAME}")
async def menu_music_library(message: Message, bot: Bot):
    """Отравляет главное меню модуля music_library."""

    await delete_previous_message(bot=bot, message=message)

    chat_id: int = message.chat.id

    await message.answer(
        text=user_messages.MAIN_MENU,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=chat_id,
        photo=settings.MENU_IMAGE_FILE_ID,
        caption=settings.MENU_CALLBACK_TEXT,
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(F.text == user_messages.USER_CANCEL_TEXT)
async def music_library_cancel_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """Отменяет все действия для модуля music_library."""

    current_state = await state.get_state()
    if not current_state:
        return

    data = await state.get_data()
    collection_songs = data.get("collection_songs")
    telegram: int = message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await state.clear()
    if collection_songs:  # Возвращаемся к сборнику песен пользователя

        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(telegram=telegram)

        await state.clear()
        if result.ok and not result.empty:
            await show_user_collection(
                user_response=result.data,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                bot=bot,
                chat_id=telegram,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                photo_file_id=settings.COLLECTION_SONGS_PHOTO_FILE_ID,
                message=user_messages.USER_CANCEL_MESSAGE,
            )
        if result.ok and result.empty:  # если пустой сборник
            await bot.send_photo(
                chat_id=telegram,
                photo=settings.COLLECTION_SONGS_PHOTO_FILE_ID,
                caption=user_messages.THERE_ARE_NO_SONGS,
                reply_markup=get_buttons_for_song_collection_empty_user(),
            )

        return

    await message.answer(
        text=f"{user_messages.USER_CANCEL_MESSAGE}\n\n{user_messages.MAIN_MENU}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=settings.MENU_CALLBACK_TEXT,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.MENU_IMAGE_FILE_ID,
    )
