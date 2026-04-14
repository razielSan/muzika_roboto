from pathlib import Path
import json
from typing import Dict, List

from aiogram import Router, F, Bot
from aiogram.types import (
    CallbackQuery,
    Message,
    ReplyKeyboardRemove,
    FSInputFile,
    InputMediaPhoto,
)
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter
from pydantic import ValidationError

from app.app_utils.keyboards import get_buttons_reply_keyboard
from app.bot.modules.admin.childes.add_executor.settings import settings
from app.bot.settings import settings as bot_settings
from app.bot.filters.admin_filters import (
    AdminFilter,
    AdminCreateExecutorCallback,
    AdminCreateFullExecutorCallback,
)
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.keyboards.inlinle import get_buttons_create_executor
from app.bot.modules.admin.childes.add_executor.dto import ExecutorImportDTO
from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.modules.admin.utils.admin import get_admin_panel
from app.app_utils.fsm import async_make_update_progress
from application.use_cases.db.music_library.create_executor import CreateExecutor
from application.use_cases.db.music_library.import_executor_from_path import (
    ImportExecutorFromPath,
)
from application.use_cases.db.music_library.chek_executor_exists import (
    ChekExecutorExists,
)
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.aiogram.messages import user_messages, resolve_message
from infrastructure.db.db_helper import db_helper
from core.response.response_data import Result, LoggingData
from core.logging.api import get_loggers
from core.response.messages import telegram_emoji


router: Router = Router(name=__name__)


class FSMAddFullExecutor(StatesGroup):
    """FSM для добавления в базовый executor с альбомами."""

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
    """

    await state.set_state(FSMAddFullExecutor.photo)
    await add_photo_file_id(message, state, bot)


@router.callback_query(
    AdminFilter(),
    StateFilter(None),
    F.data == settings.MENU_CALLBACK_DATA,
)
async def start_add_executor(
    call: CallbackQuery,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Главный обработчик модуля add_executor.
    """

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption=user_messages.PRESS_ONE_OF_THE_BUTTONS,
        ),
        reply_markup=get_buttons_create_executor(),
    )


# создание исполнителя без альбомов


class FSMAddExecutorAdmin(StatesGroup):
    """FSM для сценария добавления исполнителя без альбомов."""

    name: State = State()


@router.callback_query(AdminCreateExecutorCallback.filter())
async def add_executor_without_albums(
    call: CallbackQuery, callback_data: AdminCreateExecutorCallback, state: FSMContext
):
    """Просит ввести имя исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
        ),
    )

    await state.set_state(FSMAddExecutorAdmin.name)


@router.message(FSMAddExecutorAdmin.name, F.text)
async def finish_add_executor_without_albums(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Добавляет исполнителя в БД."""

    name: str = message.text.strip()
    chat_id: int = message.chat.id
    logging_data: LoggingData = get_loggers(name=admin_settings.NAME_FOR_LOG_FOLDER)

    result: Result = await CreateExecutor(
        uow=UnitOfWork(session_factory=db_helper.session), logging_data=logging_data
    ).execute(
        name=name,
        country="неизвестно",
        genres_executor=["неизвестно"],
        user_id=None,
        photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
        photo_file_unique_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_UNIQUE_ID,
    )
    if result.ok:
        await state.clear()
        result_message: str = resolve_message(code=result.code)
        await message.answer(
            text=result_message,
            reply_markup=ReplyKeyboardRemove(),
        )
        await get_admin_panel(
            caption=user_messages.ADMIN_PANEL_CAPTION,
            chat_id=chat_id,
            bot=bot,
        )

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_EXECUTOR_NAME}"
        )


@router.message(FSMAddExecutorAdmin.name)
async def finish_add_executor_without_albums_message(
    message: Message,
):
    """Отправляет сообщение при вводе данных не в том формате."""
    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст"),
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value
        )
    )


# добавление исполнителя с альбомами


@router.callback_query(
    AdminFilter(), StateFilter(None), AdminCreateFullExecutorCallback.filter()
)
async def add_executor(
    call: CallbackQuery,
    callback_data: AdminCreateFullExecutorCallback,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Просит ввести название исполнителя с альбомами.
    """
    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
        ),
    )

    await state.set_state(FSMAddFullExecutor.name)


@router.message(FSMAddFullExecutor.name, F.text)
async def add_name(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Просит ввести страну исполнителя.

    Добавляет имя в FSM.
    """

    executor_name: str = message.text.strip()

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
    await state.update_data(name=message.text.strip())

    await message.answer(
        text=user_messages.ENTER_THE_СOUNTRY_EXECUTOR,
        reply_markup=get_buttons_reply_keyboard(
            buttons=[
                KeyboardResponse.UNKNOWN_BUTTON.value,
                KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
            ]
        ),
    )
    await message.answer(
        text=f"{user_messages.CLICK_UNKNOWN_BUTTON}\n"
        f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}",
    )
    await state.set_state(FSMAddFullExecutor.country)


@router.message(FSMAddFullExecutor.name)
async def add_name_message(message: Message) -> None:
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=user_messages.CLICK_CANCEL_BUTTON.format(
            button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value
        )
    )


@router.message(FSMAddFullExecutor.country, F.text)
async def add_country(message: Message, state: FSMContext, bot: Bot) -> None:
    """
    Просит ввести жанры исполнителя или переходит к обработчику для ввода пути,
    если есть исполнитель.

    Добавляет страну в FSM.
    """

    country: str = message.text.strip()
    logging_data: LoggingData = get_loggers(name=admin_settings.NAME_FOR_LOG_FOLDER)

    try:  # проверяем данные на валидность
        ExecutorImportDTO(
            country=country,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}\n\n"
        )

        await message.answer(
            text=f"{user_messages.ENTER_THE_СOUNTRY_EXECUTOR}\n\n"
            f"{user_messages.CLICK_UNKNOWN_BUTTON}\n"
            f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}"
        )
        return
    await state.update_data(country=country)

    # Проверяем на наличие исполнителя в базе данных
    data: Dict = await state.get_data()
    executor_name: str = data.get("name")

    result: Result = await ChekExecutorExists(
        uow=UnitOfWork(session_factory=db_helper.session), logging_data=logging_data
    ).execute(user_id=None, name=executor_name, country=country)

    if result.ok:  # если исполнитель существует то переходим сразу к добавлению пути
        if not result.empty:
            genres = result.data
            print(genres)
            await state.update_data(genres=genres)
            await go_to_photo_step(
                message=message,
                state=state,
                bot=bot,
            )
            return

    await message.answer(
        text=user_messages.ENTER_THE_GENRES,
        reply_markup=get_buttons_reply_keyboard(
            buttons=[
                KeyboardResponse.UNKNOWN_BUTTON.value,
                KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
            ]
        ),
    )
    await state.set_state(FSMAddFullExecutor.genres)


@router.message(FSMAddFullExecutor.country)
async def add_country_message(message: Message) -> None:
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=f"{user_messages.CLICK_UNKNOWN_BUTTON}\n"
        f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}",
    )


@router.message(FSMAddFullExecutor.genres, F.text)
async def add_genres(
    message: Message,
    state: FSMContext,
    bot: Bot,
) -> None:
    """
    Просит скинуть фото исполнителя.

    Добавляет жанры в FSM.
    """

    genres: List[str] = [genre.lower().strip() for genre in message.text.split(".")]
    await state.update_data(genres=genres)

    await message.answer(
        text=user_messages.ENTER_THE_PHOTO_DEFAULT,
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
        ),
    )
    await state.set_state(FSMAddFullExecutor.photo)


@router.message(FSMAddFullExecutor.genres)
async def add_genres_message(message: Message) -> None:
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        text=f"{user_messages.CLICK_UNKNOWN_BUTTON}\n"
        f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}",
    )


@router.message(FSMAddFullExecutor.photo)
async def add_photo_file_id(message: Message, state: FSMContext, bot: Bot):
    """
    Просит ввести путь до альбомов исполнителя.

    Добавляет фото в FSM.
    """

    if message.photo:  # если сообщение является фотографией
        await state.update_data(file_id=message.photo[-1].file_id)
        await state.update_data(file_unique_id=message.photo[-1].file_unique_id)
    else:  # если нет используем базовые фото для исполнителя
        await state.update_data(file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID)
        await state.update_data(
            file_unique_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_UNIQUE_ID
        )

    await message.answer(
        text=user_messages.ENTER_THE_FULL_ALBUM_PATH,
        reply_markup=get_reply_cancel_button(
            cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
        ),
    )
    await state.set_state(FSMAddFullExecutor.path)


@router.message(FSMAddFullExecutor.path, F.text)
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

    # Формируем данные для добавления в БД
    data: Dict = await state.get_data()

    path: Path = Path(message.text)
    executor_name: str = data.get("name")
    country: str = data.get("country")
    genres: List[str] = data.get("genres")
    file_id: str = data.get("file_id")
    file_unique_id: str = data.get("file_unique_id")
    logging_data: LoggingData = get_loggers(name=admin_settings.NAME_FOR_LOG_FOLDER)

    try:  # проверяем данные на валидность
        ExecutorImportDTO(
            base_path=path,
        )
    except ValidationError as err:
        msg: Dict = json.loads(err.json())[0].get("msg")
        await message.answer(
            text=f"{telegram_emoji.yellow_triangle_with_exclamation_mark} {msg}",
            reply_markup=get_reply_cancel_button(
                cancel_button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value,
            ),
        )
        await message.answer(
            text=f"{user_messages.ENTER_THE_FULL_ALBUM_PATH}\n"
            f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}"
        )
        return

    async def get_audio_telegram(
        audio_path: Path,
        album_name: str,
        year: int,
    ) -> Message:
        """
        Отправляет в телеграм песню и возвращает полученный ответ, для получения
        file_id песни.
        """

        await bot.send_message(
            chat_id=message.chat.id,
            text=user_messages.ADD_SONGS_MESSAGE.format(
                year=year, title=album_name, song=audio_path.stem
            ),
        )
        msg: Message = await bot.send_audio(
            chat_id=chat_id,
            audio=FSInputFile(path=audio_path),
            request_timeout=1000,
        )
        await bot.send_message(
            chat_id=chat_id,
            text=user_messages.ADD_SONGS_COMPLETE.format(
                year=year, title=album_name, song=audio_path.stem
            ),
        )
        return msg

    # Для отправки сообщений при запросе и избежания спама
    await state.update_data(processing=True)
    await state.set_state(FSMAddFullExecutor.processing)
    await bot.send_message(
        chat_id=chat_id,
        text=user_messages.WAIT_MESSAGE,
        reply_markup=get_buttons_reply_keyboard(
            buttons=[KeyboardResponse.CANCEL_TEXT_UPLOAD_EXECUTOR]
        ),
    )

    # Функция для отслежвания состояние отмены
    update_progress = async_make_update_progress(state=state)

    result = await ImportExecutorFromPath(
        uow=UnitOfWork(session_factory=db_helper.session), logging_data=logging_data
    ).execute(
        executor_name=executor_name,
        country=country,
        base_path=path,
        genres=genres,
        file_id=file_id,
        file_unique_id=file_unique_id,
        audio_extensions=bot_settings.AUDIO_EXTENSIONS,
        update_progress=update_progress,
        album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
        album_defautl_photo_file_unique_id=bot_settings.ALBUM_DEFAULT_PHOTO_UNIQUE_ID,
        get_audio_telegram=get_audio_telegram,
    )

    await state.clear()
    if result.ok:
        result_message: str = resolve_message(result.code)
    else:
        result_message: str = resolve_message(result.error.code)

    await message.answer(text=result_message, reply_markup=ReplyKeyboardRemove())
    await bot.send_photo(
        chat_id=message.chat.id,
        reply_markup=get_keyboards_menu_buttons,
        photo=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
        caption=user_messages.ADMIN_PANEL_CAPTION,
    )


@router.message(FSMAddFullExecutor.path)
async def add_executor_base_message(message: Message) -> None:
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(
        f"{user_messages.CLICK_CANCEL_BUTTON.format(button=KeyboardResponse.ADMIN_CANCEL_BUTTON.value)}",
    )


@router.message(FSMAddFullExecutor.processing)
async def processing_message(message: Message, state: FSMContext) -> None:
    """
    Отправляют сообщение при вводе данных во время обработки запроса или
    отменяет запрос при нажатии кнопки.
    """

    if message.text == KeyboardResponse.CANCEL_TEXT_UPLOAD_EXECUTOR.value:
        await message.answer(
            text="Запрос на отмену принят..Дождитесь завершения добавления песен в текущий альбом..."
        )

        await state.update_data(cancel=True)
        return

    await message.answer(
        text=f"{KeyboardResponse.CANCEL_TEXT_UPLOAD_EXECUTOR.value}: Отменить скачивание исполнителя"
    )
