from typing import Dict

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.modules.music_library.services.collection_songs import show_user_collection
from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.settings import settings as music_library_settings
from application.use_cases.db.collection_songs.update_title_song import (
    UpdateTitleSongCollectionSongs,
)
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from application.use_cases.db.collection_songs.update_user_collection_songs_photo_file_id import (
    UpdateUserCollectionSongsPhotoFileId,
)
from domain.entities.db.models.user import User as UserDomain
from domain.entities.response import UserCollectionSongsResponse
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.filters import UpdateCallbackDataFilters
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_COLLECTION_SONGS,
    resolve_message,
)
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from core.utils.chek import check_number_is_positivity
from core.response.response_data import Result
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result


router: Router = Router(name=__name__)


# обновлние имени сборника песен
class FSMUpdateTitleCollectionSong(StatesGroup):
    """FSM для сценария обновления имени песни."""

    collection_songs: State = State()  # для возвращения к сборнику песен при отмене
    title: State = State()
    position: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.SongTitleCollectionSongs.filter()
)
async def start_update_song_title(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.SongTitleCollectionSongs,
    state: FSMContext,
):
    """Просит пользователя ввести имя песни."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_SONG_NAME, reply_markup=get_reply_cancel_button()
    )
    await state.update_data(collection_songs=True)
    await state.set_state(FSMUpdateTitleCollectionSong.title)


@router.message(FSMUpdateTitleCollectionSong.title, F.text)
async def add_title(message: Message, state: FSMContext):
    """Просит ввести позицию песни."""

    await message.answer(text=user_messages.ENTER_THE_SONG_POSITION)

    await state.update_data(title=message.text)
    await state.set_state(FSMUpdateTitleCollectionSong.position)


@router.message(FSMUpdateTitleCollectionSong.title)
async def add_title_message(message: Message):
    """Отправляет сообщение при вводе не требуемых данных."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


@router.message(FSMUpdateTitleCollectionSong.position, F.text)
async def finish_update_song_title(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: UserDomain,
):
    """Обновляет имя песни."""

    result_chek: Result = check_number_is_positivity(number=message.text)
    if not result_chek.ok:  # проверяет что позиция песни целое число больше 0
        error_message: str = result_chek.error.message
        await message.answer(
            f"{error_message}\n\n{user_messages.ENTER_THE_SONG_POSITION}"
        )
        return
    data: Dict = await state.get_data()

    chat_id: int = message.chat.id
    title: str = data.get("title", "unknown")
    position: int = result_chek.data
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_update: Result = await UpdateTitleSongCollectionSongs(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(user_id=user.id, title=title, position=position)
    if result_update.ok:

        if result_update.empty:  # Если позиция песни не была найдена
            msg_update = resolve_message(code=result_update.code)
            msg_update = msg_update.format(position=position)

            await message.answer(
                text=f"{msg_update}\n\n{user_messages.ENTER_THE_SONG_POSITION}"
            )
            return

        msg_update: str = resolve_message(code=result_update.code)
        msg_update: str = msg_update.format(title=title)
        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(user=user)

        await state.clear()
        if result.ok:
            await show_user_collection(
                user_response=result.data,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                start_collection_songs=0,
                bot=bot,
                chat_id=chat_id,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                message=msg_update,
            )

            return
        if not result.ok:
            error_message = resolve_message(code=result.error.code)
            await get_inline_menu_music_library(
                chat_id=chat_id,
                bot=bot,
                message=error_message,
                caption=user_messages.MAIN_MENU,
            )

    if not result_update.ok:
        await state.clear()
        error_message = resolve_message(code=result_update.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            message=error_message,
            caption=user_messages.MAIN_MENU,
        )


@router.message(FSMUpdateTitleCollectionSong.position)
async def finish_update_song_title_message(message: Message):
    """Отправляет сообщение при вводе не требуемых данных."""
    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


# обновление фотографии сборника песен
class FSMUpdateUserCollectionSongsPhotoFileId(StatesGroup):
    """FSM для сценария обновления фото сборника песен."""

    collection_songs: State = State()
    photo_file_id: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserCollectionSongsPhotoFileId.filter()
)
async def start_update_user_collection_songs_photo_file_id(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserCollectionSongsPhotoFileId,
    state: FSMContext,
):
    """Просит пользователя скинуть фотографию."""

    await state.update_data(collection_songs=True)
    await state.set_state(FSMUpdateUserCollectionSongsPhotoFileId.photo_file_id)

    await call.message.edit_reply_markup(reply_markup=None)
    await call.message.answer(
        text=user_messages.DROP_THE_PHOTO,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateUserCollectionSongsPhotoFileId.photo_file_id, F.photo)
async def finish_update_user_collection_songs_photo_file_id(
    message: Message,
    state: FSMContext,
    bot: Bot,
    user: UserDomain,
):
    """Обновляет фото сборника песен."""

    chat_id: int = message.from_user.id
    photo_file_id: str = message.photo[-1].file_id
    photo_file_unique_id: str = message.photo[-1].file_unique_id
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_update = await UpdateUserCollectionSongsPhotoFileId(
        uow=UnitOfWork(),
        logging_data=logging_data,
    ).execute(
        user_id=user.id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
    )
    await state.clear()
    if result_update.ok:

        msg_update: str = resolve_message(code=result_update.code)

        result = await GetUserCollectionSongs(
            uow=UnitOfWork(), logging_data=logging_data
        ).execute(user=user)
        if result.ok:
            user_response: UserCollectionSongsResponse = result.data

            # Обновляем photo_file_id на измененные
            user_response.collection_songs_photo_file_id = photo_file_id
            user_response.collection_songs_photo_file_unique_id = photo_file_unique_id
            await show_user_collection(
                user_response=user_response,
                bot=bot,
                chat_id=chat_id,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                message=msg_update,
            )
            return
        if not result.ok:
            error_message = resolve_message(code=result.error.code)
            await get_inline_menu_music_library(
                chat_id=chat_id,
                bot=bot,
                message=error_message,
                caption=user_messages.MAIN_MENU,
            )

    if not result_update.ok:
        error_message = resolve_message(code=result_update.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            message=error_message,
            caption=user_messages.MAIN_MENU,
        )


@router.message(FSMUpdateUserCollectionSongsPhotoFileId.photo_file_id)
async def finish_update_user_collection_songs_photo_file_id_message(message: Message):
    """Отправляет сообщение при вводе данных не в требуемом формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="фото")
    )
