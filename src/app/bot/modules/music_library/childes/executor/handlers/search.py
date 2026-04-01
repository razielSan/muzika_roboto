from typing import Dict, List
from dataclasses import dataclass

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, Message, InputMediaPhoto, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.helpers.executor import return_to_executor_page_callback
from app.bot.modules.music_library.childes.executor.keyboards.inline import (
    select_search_keyboard,
    show_executor_search,
    select_executor_genres_keybord,
)
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
    callback_update_menu_inline_music_library,
)
from application.use_cases.db.music_library.search_executor_by_name import (
    SearchExecutorName,
)
from application.use_cases.db.music_library.search_executor_by_genre import (
    SearchExecutorGenre,
)
from domain.entities.response import ExecutorSearchResponse, LibraryMode
from application.use_cases.db.music_library.get.get_executor_page import GetExecutorPage
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.db.utils.editing import get_information_executor
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.filters import Search, ScrollingCallbackDataFilters
from infrastructure.aiogram.messages import (
    user_messages,
    resolve_message,
    LIMIT_ALBUMS,
    LIMIT_SEARCH_EXECUTOR,
    GENRES,
)
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result

router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), Search.Executor.filter())
async def search_executor(
    call: CallbackQuery,
    callback_data: Search.Executor,
):
    """Отправляет клавиатуру поиска исполнителей."""

    await call.message.edit_media(
        InputMediaPhoto(
            media=music_library_settings.MENU_IMAGE_FILE_ID,
            caption=user_messages.USER_PANEL_CAPTION,
        ),
        reply_markup=select_search_keyboard(),
    )


class FSMSearchExecutor(StatesGroup):
    executors: State = State()
    name: State = State()
    search_executor: State = (
        State()
    )  # для отправки сообщения при возвращении к главной панели
    processing: State = State()


@dataclass
class SearchExecutorData:
    executors: List[ExecutorSearchResponse]
    search_executor: bool
    name: None
    processing: None


# Поиск исполнителя по имени


@router.callback_query(StateFilter(None), Search.ExecutorName.filter())
async def start_search_executor_by_name(
    call: CallbackQuery, callback_data: CallbackQuery, state: FSMContext
):
    """Просит ввести имя исполнителя."""

    await call.message.edit_reply_markup(reply_markup=None)

    await state.set_state(FSMSearchExecutor.name)
    await call.message.answer(
        text=user_messages.ENTER_THE_EXECUTOR_NAME,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMSearchExecutor.name, F.text)
async def show_find_executors(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Отправляет инлайн клавиатуру из найденных исполнителей."""

    name_lower: str = message.text.casefold().strip()
    chat_id: str = message.chat.id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await SearchExecutorName(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        name_lower=name_lower,
        user_id=None,
        len_name=5,
    )

    if result.ok:
        if result.empty:  # если не было найдено
            not_found_message: str = resolve_message(code=result.code)
            await message.answer(
                text=f"{not_found_message}\n\n{user_messages.ENTER_THE_EXECUTOR_NAME}"
            )
            return

        executors: ExecutorSearchResponse = result.data
        await state.update_data(
            SearchExecutorData(
                executors=executors,
                search_executor=True,
                name=None,
                processing=None,
            ).__dict__
        )
        await state.set_state(FSMSearchExecutor.processing)

        total: int = len(executors)
        executors = executors[0:LIMIT_SEARCH_EXECUTOR]
        await bot.send_photo(
            caption=user_messages.USER_PANEL_CAPTION,
            chat_id=chat_id,
            photo=music_library_settings.MENU_IMAGE_FILE_ID,
            reply_markup=show_executor_search(
                executors=executors,
                position=0,
                limit=LIMIT_SEARCH_EXECUTOR,
                total=total,
            ),
        )

    if not result.ok:
        await state.clear()
        error_message = resolve_message(code=result.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMSearchExecutor.name)
async def show_find_executors_message(
    message: Message,
):
    """Отправляет сообщение если были введены не те данные."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )
    await message.answer(text=user_messages.ENTER_THE_EXECUTOR_NAME)


# поиск по жанру
@router.callback_query(StateFilter(None), Search.ExecutorGenres.filter())
async def search_executor_by_genres(
    call: CallbackQuery,
    callback_data: Search.ExecutorGenres.filter(),
):
    """Отправляет инлайн клавиатуру жанров для поиска."""

    await call.message.edit_media(
        InputMediaPhoto(
            media=music_library_settings.MENU_IMAGE_FILE_ID,
            caption=user_messages.USER_PANEL_CAPTION,
        ),
        reply_markup=select_executor_genres_keybord(quantity_button=3),
    )


@router.callback_query(StateFilter(None), Search.ExecutorGenreButton.filter())
async def show_executors_search_by_genres(
    call: CallbackQuery,
    callback_data: Search.ExecutorGenreButton,
    state: FSMContext,
):
    """Отправляет найденных исполнителей по жанру."""

    order: int = callback_data.order
    genre: str = GENRES.get(order)

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await SearchExecutorGenre(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        title=genre,
        user_id=None,
    )
    if result.ok:
        await call.message.answer(
            text=user_messages.SEARCH_RESULT,
            reply_markup=get_reply_cancel_button(),
        )

        executors: ExecutorSearchResponse = result.data
        await state.update_data(
            SearchExecutorData(
                executors=executors,
                search_executor=True,
                name=None,
                processing=None,
            ).__dict__
        )
        await state.set_state(FSMSearchExecutor.processing)

        total: int = len(executors)
        executors = executors[0:LIMIT_SEARCH_EXECUTOR]
        await call.message.edit_media(
            InputMediaPhoto(
                media=music_library_settings.MENU_IMAGE_FILE_ID,
                caption=user_messages.USER_PANEL_CAPTION,
            ),
            reply_markup=show_executor_search(
                executors=executors,
                position=0,
                total=total,
                limit=LIMIT_SEARCH_EXECUTOR,
            ),
        )

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await callback_update_menu_inline_music_library(
            call=call,
            message=error_message,
            caption=user_messages.USER_PANEL_CAPTION,
        )


# общий сценарий поиска
@router.callback_query(
    FSMSearchExecutor.processing,
    ScrollingCallbackDataFilters.SearchExecutor.filter(),
)
async def scrolling_search_executor(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.SearchExecutor,
    state: FSMContext,
):
    """Пролистывает исполнителей поиска."""

    position: int = callback_data.position + callback_data.offset
    data: Dict = await state.get_data()
    state_data: SearchExecutorData = SearchExecutorData(**data)

    executors: List[ExecutorSearchResponse] = state_data.executors
    total: int = len(executors)
    executors = executors[position : position + LIMIT_SEARCH_EXECUTOR]
    await call.message.edit_media(
        media=InputMediaPhoto(
            media=music_library_settings.MENU_IMAGE_FILE_ID,
            caption=user_messages.USER_PANEL_CAPTION,
        ),
        reply_markup=show_executor_search(
            executors=executors,
            position=position,
            total=total,
            limit=LIMIT_SEARCH_EXECUTOR,
        ),
    )


@router.callback_query(
    FSMSearchExecutor.processing,
    Search.ExecutorButton.filter(),
)
async def return_exeucor_page(
    call: CallbackQuery,
    callback_data: Search.ExecutorButton,
    state: FSMContext,
):
    """Переходит на страницу исполнителя."""

    await state.clear()
    await call.message.answer(
        text=user_messages.WAIT_MESSAGE,
        reply_markup=ReplyKeyboardRemove(),
    )

    executor_id: int = callback_data.id
    logging_data: str = get_loggers(name=music_library_settings.NAME_FOR_LOG_FOLDER)

    result: Result = await GetExecutorPage(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user_id=None, executor_id=executor_id)
    if result.ok:
        result_message: str = resolve_message(code=result.code)
        current_page_executor: int = result.data
        await return_to_executor_page_callback(
            call=call,
            uow=UnitOfWork,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            get_information_executor=get_information_executor,
            mode=LibraryMode(user_id=None),
            message=result_message,
        )
    if not result.ok:
        error_message = resolve_message(code=result.error.code)
        await callback_update_menu_inline_music_library(
            call=call,
            message=error_message,
            caption=user_messages.USER_PANEL_CAPTION,
        )


@router.message(FSMSearchExecutor.processing)
async def show_find_executors_message_message(
    message: Message,
):
    """Отправляет сообщение если были введены данные а не нажата кнопка."""

    await message.answer(text=user_messages.CLICK_ONE_OF_THE_BUTTONS_ABOVE)
    await message.answer(text=user_messages.CLICK_CANCEL_BUTTON)
