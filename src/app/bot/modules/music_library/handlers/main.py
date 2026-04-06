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
from app.bot.helpers.executor import (
    return_to_executor_page,
    return_to_executor_page_callback,
)
from app.bot.helpers.album import return_to_album_page, return_to_album_page_callback
from app.bot.keyboards.inlinle import select_admin_library_keyboard
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.modules.music_library.response import get_keyboards_menu_buttons
from app.bot.utils.delete import delete_previous_message
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from domain.entities.response import (
    UserCollectionSongsResponse,
)
from domain.entities.db.models.user import User as UserDomain
from domain.entities.response import LibraryMode, LibraryRole
from infrastructure.aiogram.messages import user_messages
from infrastructure.aiogram.filters import (
    BackMenuUserPanel,
    BackExecutorPage,
    BackAlbumPage,
)
from infrastructure.aiogram.messages import (
    LIMIT_COLLECTION_SONGS,
    LIMIT_ALBUMS,
    LIMIT_SONGS,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.fsm.keys import FSMFlags
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.aiogram.response import KeyboardResponse
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers


router: Router = Router(name=settings.SERVICE_NAME)


@router.message(StateFilter(None), F.text == f"/{settings.SERVICE_NAME}")
async def menu_music_library(message: Message, bot: Bot):
    """Отправляет главное меню модуля music_library."""

    await delete_previous_message(bot=bot, message=message)

    chat_id: int = message.chat.id

    await get_inline_menu_music_library(
        chat_id=chat_id,
        bot=bot,
        caption=user_messages.USER_PANEL_CAPTION,
        message=user_messages.MAIN_MENU,
    )


@router.message(F.text == KeyboardResponse.USER_CANCEL_BUTTON.value)
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

    collection_songs: Optional[bool] = data.get(FSMFlags.COLLECTION_SONGS)
    music_library_executor: Optional[bool] = data.get(FSMFlags.MUSIC_LIBRARY_EXECUTOR)
    music_library_album: Optional[bool] = data.get(FSMFlags.MUSIC_LIBRARY_ALBUM)
    search_executor: Optional[bool] = data.get(
        FSMFlags.SEARCH_EXECUTOR
    )  # сценацрия при поиске исполнителей
    deleting_songs: Optional[bool] = data.get(
        FSMFlags.DELETING_SONGS
    )  # сценария при удалении песен
    is_admin: Optional[bool] = data.get(FSMFlags.IS_ADMIN)

    user_id: int = user.id

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

    if music_library_executor:  # возращает на страницу исполнителя
        role: LibraryMode.role = LibraryRole.USER
        if is_admin:
            role: LibraryMode.role = LibraryRole.ADMIN
            user_id = None

        current_page_executor: int = data.get(FSMFlags.CURRENT_PAGE_EXECUTOR)
        role: LibraryMode.role = LibraryRole.ADMIN if is_admin else LibraryRole.USER
        await return_to_executor_page(
            chat_id=chat_id,
            current_page_executor=current_page_executor,
            get_information_executor=get_information_executor,
            bot=bot,
            uow=UnitOfWork,
            logging_data=logging_data,
            album_position=0,
            limit_albums=LIMIT_ALBUMS,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            message=user_messages.USER_CANCEL_MESSAGE,
            mode=LibraryMode(
                user_id=user_id,
                role=role,
            ),
        )
        return

    if music_library_album or deleting_songs:  # возращает на страницу альбома
        if is_admin:
            user_id = None

        current_page_executor: int = data.get(FSMFlags.CURRENT_PAGE_EXECUTOR)
        album_id: int = data.get(FSMFlags.ALBUM_ID)
        executor_id: int = data.get(FSMFlags.EXECUTOR_ID)
        is_global_executor: bool = data.get(FSMFlags.IS_GLOBAL_EXECUTOR)
        album_position: int = data.get(FSMFlags.ALBUM_POSITION)

        await return_to_album_page(
            bot=bot,
            chat_id=chat_id,
            message=user_messages.USER_CANCEL_MESSAGE,
            user_id=user_id,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            logging_data=logging_data,
            uow=UnitOfWork,
            current_page_executor=current_page_executor,
            get_information_album=get_information_album,
            song_position=0,
            limit_songs=LIMIT_SONGS,
            album_id=album_id,
            executor_id=executor_id,
            is_global_executor=is_global_executor,
            album_position=album_position,
            is_admin=is_admin,
        )
        return
    if search_executor and is_admin:
        await bot.send_message(
            chat_id=chat_id,
            text=user_messages.USER_CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )
        await bot.send_photo(
            chat_id=message.chat.id,
            caption=user_messages.ADMIN_PANEL_CAPTION,
            reply_markup=select_admin_library_keyboard(is_admin=True),
            photo=bot_settings.ADMIN_PANEL_PHOTO_FILE_ID,
        )
        return

    # возвращаемся к главному меню модуля
    await message.answer(
        text=f"{user_messages.USER_CANCEL_MESSAGE}\n\n{user_messages.MAIN_MENU}",
        reply_markup=ReplyKeyboardRemove(),
    )

    await bot.send_photo(
        chat_id=message.chat.id,
        caption=user_messages.USER_PANEL_CAPTION,
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
    collection_songs: Optional[bool] = data.get(FSMFlags.COLLECTION_SONGS)
    search_executor: Optional[bool] = data.get(FSMFlags.SEARCH_EXECUTOR)
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    await state.clear()
    await call.message.delete_reply_markup()

    if collection_songs:
        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(user=user)

        if result:
            user_response: UserCollectionSongsResponse = result.data

            await callback_show_user_collection(
                call=call,
                user_response=user_response,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
            )

            return

    if search_executor:
        await call.message.answer(
            text=user_messages.MAIN_MENU,
            reply_markup=ReplyKeyboardRemove(),
        )

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=settings.MENU_IMAGE_FILE_ID,
            caption=user_messages.USER_PANEL_CAPTION,
        ),
        reply_markup=get_keyboards_menu_buttons,
    )


@router.callback_query(BackExecutorPage.filter())
async def get_executor_page_panel(
    call: CallbackQuery,
    callback_data: BackExecutorPage,
    state: FSMContext,
):
    """Сценария для показа исполнителя с альбомами при нажатии инлайн-кнопки возврата."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id: Optional[int] = callback_data.user_id
    album_position: int = callback_data.album_position
    current_page_executor: int = callback_data.current_page
    is_admin: bool = callback_data.is_admin
    role: LibraryRole = LibraryRole.ADMIN if is_admin else LibraryRole.USER

    await state.clear()
    await return_to_executor_page_callback(
        call=call,
        logging_data=logging_data,
        uow=UnitOfWork,
        mode=LibraryMode(
            user_id=user_id,
            role=role,
        ),
        get_information_executor=get_information_executor,
        executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        limit_albums=LIMIT_ALBUMS,
        album_position=album_position,
        current_page_executor=current_page_executor,
    )


@router.callback_query(BackAlbumPage.filter())
async def get_album_page(
    call: CallbackQuery, callback_data: BackAlbumPage, state: FSMContext
):
    """Сценария для альбома с песнями при нажатии инлайн-кнопки возврата."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    user_id: Optional[int] = callback_data.user_id
    album_position: int = callback_data.album_position
    current_page_executor: int = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    is_global_executor: bool = callback_data.is_global_executor
    executor_id: int = callback_data.executor_id
    is_admin: bool = callback_data.is_admin

    data: Dict = await state.get_data()
    deleting_songs: bool = data.get(FSMFlags.DELETING_SONGS)
    if (
        deleting_songs
    ):  # отравляем сообщение при удалении песен, для удаления клавиатуры
        await call.message.answer(
            text=user_messages.USER_CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

    await state.clear()
    await return_to_album_page_callback(
        call=call,
        uow=UnitOfWork,
        logging_data=logging_data,
        user_id=user_id,
        album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
        album_position=album_position,
        album_id=album_id,
        current_page_executor=current_page_executor,
        get_information_album=get_information_album,
        executor_id=executor_id,
        song_position=0,
        is_global_executor=is_global_executor,
        message=user_messages.BACK_ALBUM_PAGE,
        limit_songs=LIMIT_SONGS,
        is_admin=is_admin,
    )
