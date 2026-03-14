from typing import Dict, Optional

from aiogram import Router, F, Bot
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext

from app.bot.modules.music_library.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.modules.music_library.services.collection_songs import (
    show_user_collection,
    callback_show_user_collection,
)
from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from app.bot.utils.delete import delete_previous_message
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from domain.entities.response import (
    UserCollectionSongsResponse,
)
from domain.entities.db.models.user import User as UserDomain
from infrastructure.aiogram.messages import user_messages
from infrastructure.aiogram.filters import BackMenuUserPanel, BackExecutorPage
from infrastructure.aiogram.messages import LIMIT_COLLECTION_SONGS, LIMIT_ALBUMS
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.aiogram.response import KeyboardResponse
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers


router: Router = Router(name=settings.SERVICE_NAME)


@router.message(StateFilter(None), F.text == f"/{settings.SERVICE_NAME}")
async def menu_music_library(message: Message, bot: Bot):
    """Отправляет главное меню модуля music_library."""

    await delete_previous_message(bot=bot, message=message)

    chat_id: int = message.chat.id

    await message.answer(
        text=user_messages.MAIN_MENU,
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=chat_id,
        photo=settings.MENU_IMAGE_FILE_ID,
        caption=KeyboardResponse.USER_PANEL_CAPTION,
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(F.text == user_messages.USER_CANCEL_TEXT)
async def music_library_cancel_handler(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: UserDomain,
) -> None:
    """Отменяет все действия для модуля music_library."""

    current_state = await state.get_state()
    if not current_state:
        return

    data: Dict = await state.get_data()
    collection_songs: Optional[bool] = data.get("collection_songs")

    chat_id: int = message.chat.id

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await state.clear()
    if collection_songs:  # Возвращаемся к сборнику песен пользователя

        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(user=user)
        if result.ok:
            user_response: UserCollectionSongsResponse = result.data

            await show_user_collection(
                user_response=user_response,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                bot=bot,
                chat_id=chat_id,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                message=user_messages.USER_CANCEL_MESSAGE,
            )
            return

    # возвращаемся к главному меню модуля
    await message.answer(
        text=f"{user_messages.USER_CANCEL_MESSAGE}\n\n{user_messages.MAIN_MENU}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=KeyboardResponse.USER_PANEL_CAPTION,
        reply_markup=get_keyboards_menu_buttons,
        photo=settings.MENU_IMAGE_FILE_ID,
    )


@router.callback_query(BackMenuUserPanel.filter())
async def callback_music_library_cancel_handler(
    call: CallbackQuery,
    callback_data: BackMenuUserPanel,
    state: FSMContext,
    user: UserDomain,
):
    """
    Каллбэк отмена всех действий для модуля music_library и возращение к нужной панели.
    """
    data: Dict = await state.get_data()
    collection_songs: Optional[bool] = data.get("collection_songs")
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await state.clear()
    if collection_songs:
        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(user=user)

        if result:
            user_response: UserCollectionSongsResponse = result.data

            await call.message.answer(text=user_messages.USER_CANCEL_MESSAGE)
            await callback_show_user_collection(
                call=call,
                user_response=user_response,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
            )

            return

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=settings.MENU_IMAGE_FILE_ID,
            caption=KeyboardResponse.USER_PANEL_CAPTION,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )


@router.callback_query(BackExecutorPage.filter())
async def get_executor_page_panel(
    call: CallbackQuery,
    callback_data: BackExecutorPage,
):
    """Сценария для показа исполнителя с альбомами при нажатии кнопки возврата."""

    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id = callback_data.user_id
    album_position = callback_data.album_position
    current_page_executor = callback_data.current_page

    await ShowExecutorPageService(
        uow=UnitOfWork,
        logging_data=logging_data,
        call=call,
    ).execute(
        user_id=user_id,
        get_information_executor=get_information_executor,
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        limit_albums=LIMIT_ALBUMS,
        album_position=album_position,
        current_page=current_page_executor,
    )
