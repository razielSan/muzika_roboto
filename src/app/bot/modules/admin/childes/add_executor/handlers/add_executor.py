from pathlib import Path
import json
from typing import Dict, List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from pydantic import ValidationError

from app.bot.modules.admin.childes.add_executor.services.add_executor import (
    add_executor_service,
)
from app.bot.modules.admin.childes.add_executor.keyboards.reply import (
    get_reply_add_executor_button,
)
from app.app_utils.keyboards import get_reply_cancel_button
from app.bot.modules.admin.childes.add_executor.settings import settings
from app.bot.settings import settings as bot_settings
from core.response.messages import telegram_emoji, messages
from app.bot.filters.admin_filters import AdminFilter
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.childes.add_executor.dto import ExecutorImportDTO
from app.bot.modules.admin.settings import settings as admin_settings
from infrastructure.aiogram.response import format_album
from app.app_utils.fsm import async_make_update_progress
from core.response.response_data import Result


router: Router = Router(name=__name__)


class FSMAddExecutor(StatesGroup):
    """FSM для добавления в базовый executor."""

    name: State = State()
    country: State = State()
    genres: State = State()
    photo: State = State()
    file_id: State = State()  # используется для сохранения file_id фото(не состояние)
    file_unique_id: State = (
        State()
    )  # используется для сохранен file_unique_id фото(не состояние)
    path: State = State()
    processing: State = State()
    cancel: State = State()


async def go_to_photo_step(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Переходит в функцию add_photo_file_id.

    Встает в состояние FSMAddExecutor.photo.
    """

    await state.set_state(FSMAddExecutor.photo)
    await add_photo_file_id(message, state, bot)


@router.callback_query(
    AdminFilter(),
    StateFilter(None),
    F.data == settings.MENU_CALLBACK_DATA,
)
async def add_executor(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Главный обработчик модуля add_executor.

    Работа с FSMAddExecutor.
    Встает в состоние FSMAddExecutor.name
    """

    await call.message.answer(
        f"{telegram_emoji.pencil} Введите название исполнителя\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
    await call.message.edit_reply_markup(reply_markup=None)

    try:  # Удаляем админ панель
        await bot.delete_message(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
        )
    except Exception:
        pass

    await state.set_state(FSMAddExecutor.name)


@router.message(FSMAddExecutor.processing, F.text)
async def processing_message(message: Message, state: FSMContext) -> None:
    """
    Отправляют сообщение при вводе текста во время обработки запроса или
    отменяет запрос при нажатии кнопки.

    Работа с FSMAddExecutor.
    """

    if message.text == messages.CANCEL_TEXT_UPLOAD_EXECUTOR:
        await message.answer(
            text="Запрос на отмену принят..Дождитесь завершения добавления песен в текущий альбом..."
        )

        await state.update_data(cancel=True)
        return

    await message.answer(text=messages.WAIT_AND_CANCEL_MESSAGE)


@router.message(FSMAddExecutor.name, F.text)
async def add_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Просит ввести страну исполнителя.

    Работа с FSMAddExecutor.
    Встает в состояние FSMAddExecutor.country.
    """
    try:  # удаляем предыдущее сообщение
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass
    executor_name = message.text.lower().strip()

    try:  # проверяем данные на валидность
        ExecutorImportDTO(
            executor_name=executor_name,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}\n\n"
            f"{telegram_emoji.pencil} Введите,снова, название исполнителя"
        )
        return
    await state.update_data(name=message.text.lower().strip())

    await message.answer(
        text=f"{telegram_emoji.pencil} Введите страну исполнителя\n\n"
        f"{messages.UNKNOWN_TEXT}: Название по умолчанию\n"
        f"{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_add_executor_button(),
    )
    await state.set_state(FSMAddExecutor.country)


@router.message(FSMAddExecutor.country, F.text)
async def add_country(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Просит ввести жанры исполнителя или переходит к обработчику для ввода пути,
    если есть исполнитель.

    Работа с FSMAddExecutor.
    Встает в состояние FSMAddExecutor.genres.
    """

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    country: str = message.text.strip().lower()

    try:  # проверяем данные на валидность
        ExecutorImportDTO(
            country=country,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}\n\n"
            f"{telegram_emoji.pencil} Введите,снова, страну исполнителя\n\n"
            f"{messages.UNKNOWN_TEXT}: Название по умолчанию\n",
            f"{messages.CANCEL_TEXT}: Отмена",
        )
        return
    await state.update_data(country=country)

    # Проверяем на наличие исполнителя в базе данных
    data: Dict = await state.get_data()
    executor_name: str = data.get("name")

    result = await add_executor_service.chek_executor_exists(
        executor_name=executor_name,
        country=country,
    )

    if result.ok:  # если исполнитель существует то переходим сразу к добавлению пути
        genres = result.data
        await state.update_data(genres=genres)
        await go_to_photo_step(
            message=message,
            state=state,
            bot=bot,
        )
        return

    await message.answer(
        text=f"{telegram_emoji.pencil} Введите жанры исполнителя через точку"
        "\n\nПример: панк-рок.металл\n\n"
        f"{messages.UNKNOWN_TEXT}: Название по умолчанию\n"
        f"{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_add_executor_button(),
    )
    await state.set_state(FSMAddExecutor.genres)


@router.message(FSMAddExecutor.genres, F.text)
async def add_genres(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Просит скинуть фото исполнителя.

    Работа с FSMAddExecutor.
    Встает в состояние FSMAddExecutor.photo.
    """

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    genres: List[str] = [genre.lower().strip() for genre in message.text.split(".")]
    await state.update_data(genres=genres)

    await message.answer(
        text=f"{telegram_emoji.pencil} Скидывайте фотографию"
        f" исполнителя или напечатайте любой символ\n\n{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMAddExecutor.photo)


@router.message(FSMAddExecutor.photo)
async def add_photo_file_id(message: Message, state: FSMContext, bot: Bot):
    """
    Просит ввести путь до альбомов исполнителя.

    Работа с FSMAddExecutor.
    Встает в состояние FSMAddExecutor.path.
    """

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    if message.photo:  # если сообщение является фотографией
        await state.update_data(file_id=message.photo[-1].file_id)
        await state.update_data(file_unique_id=message.photo[-1].file_unique_id)
    else:  # если нет используем базовые фото для исполнителя
        await state.update_data(file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID)
        await state.update_data(
            file_unique_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_UNIQUE_ID
        )

    await message.answer(
        text=f"{telegram_emoji.pencil} Введите путь до альбома с исполнителем\n\n"
        f"Формат имени альбома: {format_album.FORMAT_ALBUM}\n"
        f"{messages.CANCEL_TEXT}: Отмена",
        reply_markup=get_reply_cancel_button(),
    )
    await state.set_state(FSMAddExecutor.path)


@router.message(FSMAddExecutor.path)
async def add_executor_base(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Добавляет исполителя с альбомами в базу данных.
    """

    # Формируем общие данные
    chat_id: int = message.chat.id

    try:
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        await bot.delete_message(
            chat_id=message.chat.id, message_id=message.message_id - 1
        )
    except Exception:
        pass

    # Формируем данные для добавления в БД
    data: Dict = await state.get_data()

    path: Path = Path(message.text)
    executor_name: str = data.get("name")
    country: str = data.get("country")
    genres: List[str] = data.get("genres")
    file_id: str = data.get("file_id")
    file_unique_id: str = data.get("file_unique_id")

    try:  # проверяем данные на валидность
        ExecutorImportDTO(
            base_path=path,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            text=f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}"
            "\n\nВведите, снова, путь до альбома с исполнителем\n"
            f"{messages.CANCEL_TEXT}: Отмена",
            reply_markup=get_reply_cancel_button(),
        )
        return

    async def get_audio_telegram(audio_path: Path, album_name: str) -> Message:
        """
        Отправляет в телеграм песню и возвращает полученный ответ, для получения
        file_id песни.
        """

        await bot.send_message(
            chat_id=message.chat.id,
            text=f"Идет добавление песни {audio_path.stem} в альбом {album_name}",
        )
        msg: Message = await bot.send_audio(
            chat_id=chat_id,
            audio=FSInputFile(path=audio_path),
            request_timeout=1000,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=f"Альбом {album_name}. Песня {audio_path.stem} добавлена",
        )
        return msg

    # Для отправки сообщений при запросе и избежания спама
    await state.set_state(FSMAddExecutor.processing)
    await bot.send_message(
        chat_id=chat_id,
        text=messages.WAIT_MESSAGE,
        reply_markup=get_reply_cancel_button(
            cancel_text=messages.CANCEL_TEXT_UPLOAD_EXECUTOR,
        ),
    ),

    # Функция для отслежвания состояние отмены
    update_progress = async_make_update_progress(state=state)

    result: Result = await add_executor_service.import_executor_from_path(
        executor_name=executor_name,
        country=country,
        genres=genres,
        base_path=path,
        file_id=file_id,
        file_unique_id=file_unique_id,
        get_audio_telegram=get_audio_telegram,
        audio_extensions=bot_settings.AUDIO_EXTENSIONS,
        update_progress=update_progress,
    )
    await state.clear()
    if result.ok:
        await message.answer(
            text=result.data,
            reply_markup=ReplyKeyboardRemove(),
        )
    else:
        await message.answer(
            text=result.error.message,
            reply_markup=ReplyKeyboardRemove(),
        )
    await bot.send_photo(
        chat_id=message.chat.id,
        reply_markup=get_keyboards_menu_buttons,
        photo=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
        caption=messages.ADMIN_PANEL_TEXT,
    )
