from pathlib import Path
import json
from typing import Dict

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from pydantic import ValidationError


from app.bot.modules.admin.childes.add_executor.settings import settings
from app.bot.modules.admin.childes.add_executor.services.add_executor import (
    service_add_executor,
)
from app.bot.modules.admin.childes.add_executor.keyboards.reply import (
    get_reply_add_executor_button,
)
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.settings import settings as bot_settings
from app.bot.modules.admin.childes.add_executor.settings import settings
from core.response.messages import telegram_emoji, messages
from app.bot.modules.admin.filters import AdminFilter
from app.bot.modules.admin.childes.add_executor.dto import ExecutorImportDTO
from app.bot.response import format_album
from core.logging.api import get_loggers


router = Router(name=__name__)


class FSMAddExecutor(StatesGroup):
    name: State = State()
    country: State = State()
    genres: State = State()
    photo: State = State()
    file_id: State = State()  # используется для сохранения file_id фото(не состояние)
    file_unique_id: State = (
        State()
    )  # используется для сохранен file_unique_id фото(не состояние)
    path: State = State()


@router.callback_query(
    AdminFilter(),
    F.data == settings.MENU_CALLBACK_DATA,
)
async def add_executor(
    call: CallbackQuery,
    state: FSMContext,
):
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        f"{telegram_emoji.pencil} Введите название исполнителя",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMAddExecutor.name)


@router.message(FSMAddExecutor.name, F.text == messages.CANCEL_TEXT)
@router.message(FSMAddExecutor.country, F.text == messages.CANCEL_TEXT)
@router.message(FSMAddExecutor.genres, F.text == messages.CANCEL_TEXT)
@router.message(FSMAddExecutor.photo, F.text == messages.CANCEL_TEXT)
@router.message(FSMAddExecutor.path, F.text == messages.CANCEL_TEXT)
async def cancel_handler(
    message: Message,
    bot: Bot,
    state: FSMContext,
    get_main_inline_keyboards,
):

    await state.clear()

    await message.answer(
        text=messages.CANCEL_MESSAGE, reply_markup=ReplyKeyboardRemove()
    )
    await bot.send_message(
        text=messages.START_BOT_MESSAGE,
        chat_id=message.chat.id,
        reply_markup=get_main_inline_keyboards,
    )


@router.message(FSMAddExecutor.name, F.text)
async def add_name(message: Message, state: FSMContext, bot: Bot):

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await state.update_data(name=message.text.strip())

    await message.answer(
        f"{telegram_emoji.pencil} Введите страну исполнителя или нажмите Неизвестно",
        reply_markup=get_reply_add_executor_button(),
    )
    await state.set_state(FSMAddExecutor.country)


@router.message(FSMAddExecutor.country, F.text)
async def add_country(message: Message, state: FSMContext, bot: Bot):

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    await state.update_data(country=message.text.strip())

    await message.answer(
        f"{telegram_emoji.pencil} Введите жанры исполнителя через точку"
        " или нажмите Неизвестно\n\nПример: панк-рок.металл",
        reply_markup=get_reply_add_executor_button(),
    )
    await state.set_state(FSMAddExecutor.genres)


@router.message(FSMAddExecutor.genres, F.text)
async def add_genres(message: Message, state: FSMContext, bot: Bot):

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    genres = [genre.strip() for genre in message.text.split(".")]
    await state.update_data(genres=genres)

    await message.answer(
        f"{telegram_emoji.pencil} Скидывайте фотографию исполнителя или напечатайте любой символ",
        reply_markup=get_reply_add_executor_button(),
    )
    await state.set_state(FSMAddExecutor.photo)


@router.message(FSMAddExecutor.photo)
async def photo(message: Message, state: FSMContext, bot: Bot):

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    if message.photo:
        await state.update_data(file_id=message.photo[-1].file_id)
        await state.update_data(file_unique_id=message.photo[-1].file_unique_id)
    else:
        await state.update_data(file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID)
        await state.update_data(
            file_unique_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_UNIQUE_ID
        )

    await message.answer_photo(
        photo=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID, caption="ok"
    )

    await message.answer(
        f"{telegram_emoji.pencil} Введите путь до альбома с исполнителем\n\n"
        f"Формат имени альбома: {format_album.FORMAT_ALBUM}",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMAddExecutor.path)


@router.message(FSMAddExecutor.path)
async def photo(
    message: Message,
    state: FSMContext,
    bot: Bot,
    get_main_inline_keyboards,
):

    chat_id = message.chat.id
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    path = Path(message.text)

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    data = await state.get_data()

    telegram = message.from_user.id
    executor_name = data.get("name")
    country = data.get("country")
    genres = data.get("genres")
    file_id = data.get("file_id")
    file_unique_id = data.get("file_unique_id")

    try:
        ExecutorImportDTO(
            executor_name=executor_name,
            country=country,
            genres=genres,
            file_id=file_id,
            file_unique_id=file_unique_id,
            base_path=path,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}"
        )

        await bot.send_message(
            chat_id=chat_id,
            text=messages.CANCEL_MESSAGE,
            reply_markup=ReplyKeyboardRemove(),
        )

        await bot.send_message(
            chat_id=chat_id,
            text=f"{telegram_emoji.pencil} Введите, снова, название исполнителя",
            reply_markup=get_reply_cancel_button(),
        )
        await state.set_state(FSMAddExecutor.name)

        return

    async def get_audio_telegram(audio_path: Path) -> Message:
        msg: Message = await bot.send_audio(
            chat_id=chat_id,
            audio=FSInputFile(path=audio_path),
            request_timeout=1000,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=f"Песня {audio_path.stem} добавлена",
        )
        return msg

    await bot.send_message(
        chat_id=chat_id,
        text=messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    ),

    result = await service_add_executor.import_executor_from_path(
        telegram=telegram,
        user_name=message.from_user.first_name,
        executor_name=executor_name,
        country=country,
        genres=genres,
        base_path=path,
        file_id=file_id,
        file_unique_id=file_unique_id,
        get_audio_telegram=get_audio_telegram,
        logging_data=logging_data,
        audio_extensions=bot_settings.AUDIO_EXTENSIONS,
    )
    await state.clear()
    if result.ok:
        await message.answer(text=result.data)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_inline_keyboards,
        )
    else:
        await message.answer(text=result.error.message)
        await bot.send_message(
            chat_id=chat_id,
            text=messages.START_BOT_MESSAGE,
            reply_markup=get_main_inline_keyboards,
        )
