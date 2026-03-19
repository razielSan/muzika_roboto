from typing import Optional, Dict, List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.settings import settings as bot_settings
from app.bot.helpers.executor import return_to_executor_page
from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from application.use_cases.db.music_library.update.update_photo_executor import (
    UpdatePhotoExecutor,
)
from application.use_cases.db.music_library.update.update_country_executor import (
    UpdateCountryExecutor,
)
from application.use_cases.db.music_library.update.update_genre_executor import (
    UpdateGenreExecutor,
)
from application.use_cases.db.music_library.update.update_name_executor import (
    UpdateNameExecutor,
)
from infrastructure.aiogram.filters import UpdateCallbackDataFilters
from infrastructure.aiogram.messages import user_messages, LIMIT_ALBUMS, resolve_message
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.db.uow import UnitOfWork
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers


router: Router = Router(name=__name__)

# обновления фото исполнителя


class FSMUpdateExecutorPhotoFileId(StatesGroup):
    """FSM для сценария обновления фотографии исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    user_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    photo: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorPhotoFileId.filter()
)
async def start_update_photo_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorPhotoFileId,
    state: FSMContext,
):
    """Просит скинуть фотографию исполнителя."""

    executor_id: int = callback_data.excecutor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor

    await call.message.edit_reply_markup(reply_markup=None)

    await state.update_data(executor_id=executor_id)
    await state.update_data(user_id=user_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateExecutorPhotoFileId.photo)
    await call.message.answer(
        text=user_messages.ENTER_THE_PHOTO,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateExecutorPhotoFileId.photo, F.photo)
async def end_update_photo_executor(
    message: Message,
    state: FSMContext,
    bot,
):
    """Обновляет фотографию исполнителя."""

    photo_file_id: str = message.photo[-1].file_id
    photo_file_unique_id: str = message.photo[-1].file_unique_id

    chat_id: int = message.chat.id
    update_photo_executor_data = await state.get_data()
    executor_id: int = update_photo_executor_data.get("executor_id")
    user_id: Optional[int] = update_photo_executor_data.get("user_id")
    current_page_executor: int = update_photo_executor_data.get("current_page_executor")
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    await state.clear()
    result_update_photo_executor: Result = await UpdatePhotoExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
    )
    if result_update_photo_executor.ok:
        result_message: str = resolve_message(code=result_update_photo_executor.code)
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=0,
            user_id=user_id,
        )
        return

    if not result_update_photo_executor.ok:
        error_message = resolve_message(code=result_update_photo_executor.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateExecutorPhotoFileId.photo)
async def end_update_photo_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="фото")
    )


# обновление страны исполнителя


class FSMUpdateCountryExecutor(StatesGroup):
    """FSM для сценария обновления страны исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    user_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    country: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorCountry.filter()
)
async def start_update_country_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorCountry,
    state: FSMContext,
):
    """Просит ввести страну исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    user_id: Optional[int] = callback_data.user_id
    executor_id: int = callback_data.excecutor_id
    current_page_executor: int = callback_data.current_page_executor

    await state.update_data(user_id=user_id)
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateCountryExecutor.country)

    await call.message.answer(
        text=user_messages.ENTER_THE_СOUNTRY_EXECUTOR,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateCountryExecutor.country, F.text)
async def end_update_country_executor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет страну исполнителя."""

    update_country_executor_data: Dict = await state.get_data()
    executor_id: int = update_country_executor_data.get("executor_id")
    user_id: Optional[int] = update_country_executor_data.get("user_id")
    current_page_executor: int = update_country_executor_data.get(
        "current_page_executor"
    )
    chat_id: int = message.chat.id
    country: str = message.text.strip()
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    await state.clear()
    result_update_country_executor: Result = await UpdateCountryExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        country=country,
    )
    if result_update_country_executor.ok:
        result_message: str = resolve_message(code=result_update_country_executor.code)
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=0,
            user_id=user_id,
        )
        return

    if not result_update_country_executor.ok:
        error_message: str = resolve_message(
            code=result_update_country_executor.error.code
        )
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateCountryExecutor.country)
async def end_update_country_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


# Обновление жанров исполнителя


class FSMUpdateGenresExecutor(StatesGroup):
    """FSM для сценария обновления жанров исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    user_id: State = State()
    executor_id: State = State()
    current_page_executor: State = State()
    genres: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorGenres.filter()
)
async def start_update_executor_genres(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorGenres,
    state: FSMContext,
):
    "Просит ввести жанры исполнителя."

    await call.message.edit_reply_markup(reply_markup=None)

    user_id: Optional[int] = callback_data.user_id
    executor_id: int = callback_data.excecutor_id
    current_page_executor: int = callback_data.current_page_executor

    await state.update_data(user_id=user_id)
    await state.update_data(executor_id=executor_id)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateGenresExecutor.genres)
    await call.message.answer(
        text=user_messages.ENTER_THE_GENRES,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateGenresExecutor.genres, F.text)
async def end_update_genres_executor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет жанры исполнителя."""

    update_genres_executor_data: Dict = await state.get_data()
    executor_id: int = update_genres_executor_data.get("executor_id")
    user_id: Optional[int] = update_genres_executor_data.get("user_id")
    current_page_executor: int = update_genres_executor_data.get(
        "current_page_executor"
    )
    chat_id: int = message.chat.id
    genres: List[str] = message.text.split(".")
    genres = [genre.strip() for genre in genres]
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    await state.clear()
    result_update_country_executor: Result = await UpdateGenreExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        genres=genres,
    )
    if result_update_country_executor.ok:
        result_message: str = resolve_message(code=result_update_country_executor.code)
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=0,
            user_id=user_id,
        )
        return
    if not result_update_country_executor.ok:
        error_message: str = resolve_message(
            code=result_update_country_executor.error.code
        )
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateGenresExecutor.genres)
async def end_update_genres_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


# обновляет имя исполнителя
class FSMUpdateNameExecutor(StatesGroup):
    """FSM для сценария для обновления имения исполнителя."""

    music_library_executor: State = State()  # для возратка к исполнителю при отмене
    user_id: State = State()
    executor_id: State = State()
    name: State = State()
    country: State = State()


@router.callback_query(
    StateFilter(None), UpdateCallbackDataFilters.UserExecutorName.filter()
)
async def start_update_name_executor(
    call: CallbackQuery,
    callback_data: UpdateCallbackDataFilters.UserExecutorName,
    state: FSMContext,
):
    """Просит скинуть фотографию исполнителя."""

    executor_id: int = callback_data.excecutor_id
    user_id: Optional[int] = callback_data.user_id
    country: str = callback_data.country

    await call.message.edit_reply_markup(reply_markup=None)

    await state.update_data(executor_id=executor_id)
    await state.update_data(user_id=user_id)
    await state.update_data(country=country)
    await state.update_data(music_library_executor=True)
    await state.set_state(FSMUpdateNameExecutor.name)
    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMUpdateNameExecutor.name, F.text)
async def end_update_name_excutor(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Обновляет имя исполнителя."""

    name: str = message.text.strip()
    update_name_executor_data: Dict = await state.get_data()
    executor_id: int = update_name_executor_data.get("executor_id")
    user_id: Optional[int] = update_name_executor_data.get("user_id")
    country: str = update_name_executor_data.get("country")
    chat_id: int = message.chat.id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    await state.clear()
    result_update_country_executor: Result = await UpdateNameExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user_id=user_id, executor_id=executor_id, name=name, country=country)
    if result_update_country_executor.ok:
        result_message: str = resolve_message(code=result_update_country_executor.code)
        current_page_executor: int = result_update_country_executor.data
        await return_to_executor_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            limit_albums=LIMIT_ALBUMS,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            get_information_executor=get_information_executor,
            uow=UnitOfWork,
            album_position=0,
            user_id=user_id,
        )
        return
    if not result_update_country_executor.ok:
        error_message: str = resolve_message(
            code=result_update_country_executor.error.code
        )
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMUpdateNameExecutor.name)
async def end_update_name_executor_message(message: Message):
    """Отравляет сообщение если были отправлены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
