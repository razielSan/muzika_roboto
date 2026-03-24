from typing import List

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.music_library.childes.add_user_executor.settings import settings
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from application.use_cases.db.music_library.create_executor import CreateExecutor
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.messages import user_messages, resolve_message
from infrastructure.db.uow import UnitOfWork
from core.response.response_data import LoggingData, Result
from core.logging.api import get_loggers


router: Router = Router(name=__name__)


class FSMAddExecutorML(StatesGroup):
    """FSM для сценаря добавления исполнителя пользователем"""

    name: State = State()
    country: State = State()
    genres: State = State()
    photo: State = State()


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def add_user_executor(call: CallbackQuery, state: FSMContext):
    """Просит ввести имя исполнителя."""
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMAddExecutorML.name)


@router.message(FSMAddExecutorML.name, F.text)
async def add_name(message: Message, state: FSMContext):
    """Просит ввести страну исполнителя."""
    name = message.text.strip()
    await state.update_data(name=name)
    await state.set_state(FSMAddExecutorML.country)

    await message.answer(text=user_messages.ENTER_THE_СOUNTRY_EXECUTOR)


@router.message(FSMAddExecutorML.name, F)
async def add_name_message(message: Message):
    """Отправляет сообщение при вводе данных не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


@router.message(FSMAddExecutorML.country, F.text)
async def add_country(message: Message, state: FSMContext):
    """Добавляет страну."""

    country = message.text.strip()

    await state.update_data(country=country)
    await state.set_state(FSMAddExecutorML.genres)
    await message.answer(text=user_messages.ENTER_THE_GENRES)


@router.message(FSMAddExecutorML.country, F)
async def add_country_message(message: Message):
    """Отправляет сообщение при вводе данных не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


@router.message(FSMAddExecutorML.genres, F.text)
async def add_genres(message: Message, state: FSMContext):
    """Просит скинуть фотографию."""

    genres = message.text.split(".")
    genres = [genre.strip() for genre in genres]
    await state.update_data(genres=genres)
    await state.set_state(FSMAddExecutorML.photo)
    await message.answer(text=user_messages.ENTER_THE_PHOTO_DEFAULT)


@router.message(FSMAddExecutorML.photo, F.text)
@router.message(FSMAddExecutorML.photo, F.photo)
async def add_photo(
    message: Message,
    state: FSMContext,
    bot,
    user,
):
    """Создает исполнителя."""

    if message.photo:
        photo_file_id = message.photo[-1].file_id
        photo_file_unique_id = message.photo[-1].file_unique_id
    else:
        photo_file_id = None
        photo_file_unique_id = None

    chat_id = message.chat.id
    user_executor_data = await state.get_data()
    name: str = user_executor_data.get("name")
    country: str = user_executor_data.get("country")
    genres: List[str] = user_executor_data.get("genres")

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_create_executor: Result = await CreateExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        name=name,
        country=country,
        genres_executor=genres,
        user_id=user.id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
    )

    if result_create_executor.ok:
        await state.clear()
        success_message = resolve_message(code=result_create_executor.code)
        await get_inline_menu_music_library(
            bot=bot,
            chat_id=chat_id,
            caption=user_messages.USER_PANEL_CAPTION,
            message=success_message,
        )

    if not result_create_executor.ok:
        await state.set_state(FSMAddExecutorML.name)
        error_message = resolve_message((result_create_executor.error.code))
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_EXECUTOR_NAME}"
        )


@router.message(FSMAddExecutorML.photo)
async def add_photo_message(message: Message):
    """Отправляет сообщение при вводе данных не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(
            format="текст или фото"
        )
    )
