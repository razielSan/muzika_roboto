from dataclasses import dataclass
from typing import Optional, List, Dict

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.helpers.executor import return_to_executor_page
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.helpers.album import return_to_album_page
from application.use_cases.db.music_library.add_album import AddAlbumExecutor
from application.use_cases.db.music_library.add_songs_album import AddSongsAlbum
from domain.entities.response import SongResponse, LibraryMode
from infrastructure.aiogram.filters import AddCallbackDataFilters
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_ALBUMS,
    resolve_message,
    LIMIT_SONGS,
)
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.db.uow import UnitOfWork
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from core.utils.chek import check_number_is_positivity
from core.response.response_data import Result, LoggingData
from core.logging.api import get_loggers

router: Router = Router(name=__name__)

# Добавление альбома
class FSMAddAlbumML(StatesGroup):
    """FSM для сценария добавления альбома."""

    current_page_executor: State = State()
    music_library_executor: State = State()
    executor_id: State = State()
    user_id: State = State()
    title: State = State()
    photo: State = State()
    photo_file_id: State = State()
    photo_file_unique_id: State = State()
    song_counter: State = State()
    year: State = State()
    songs: State = State()
    processing: State = State()


@dataclass
class AddAlbumData:
    current_page_executor: int
    music_library_executor: bool
    song_counter: Optional[int]
    executor_id: int
    user_id: Optional[int]
    title: str
    year: int
    photo_file_id: Optional[str]
    photo_file_unique_id: Optional[str]
    songs: List[SongResponse]
    photo: None
    processing: None


@router.callback_query(
    StateFilter(None), AddCallbackDataFilters.AddAlbumExecutor.filter()
)
async def start_add_album(
    call: CallbackQuery,
    callback_data: AddCallbackDataFilters.AddAlbumExecutor,
    state: FSMContext,
):
    """Просит ввести название альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    executor_id: int = callback_data.executor_id
    user_id: int = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor

    await state.update_data(
        AddAlbumData(
            executor_id=executor_id,
            user_id=user_id,
            song_counter=0,
            current_page_executor=current_page_executor,
            music_library_executor=True,
            songs=[],
            title="",
            year="",
            photo_file_id="",
            photo_file_unique_id="",
            photo=None,
            processing=None,
        ).__dict__
    )

    await state.set_state(FSMAddAlbumML.title)

    await call.message.answer(
        text=user_messages.ENTER_THE_ALBUM_TITLE,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMAddAlbumML.title, F.text)
async def add_title(message: Message, state: FSMContext):
    """Просит ввести год выхода альбома."""

    title: str = message.text.strip()
    await state.update_data(title=title)
    await state.set_state(FSMAddAlbumML.year)
    await message.answer(text=user_messages.ENTER_THE_ALBUM_YEAR)


@router.message(FSMAddAlbumML.title)
async def add_title_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


@router.message(FSMAddAlbumML.year, F.text)
async def add_year(message: Message, state: FSMContext):
    "Просит скинуть фото альбома."

    result_year: Result = check_number_is_positivity(number=message.text)
    if not result_year.ok:
        error_message: str = result_year.error.message
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_ALBUM_YEAR}"
        )
        return
    year: int = result_year.data
    await state.update_data(year=year)
    await state.set_state(FSMAddAlbumML.photo)
    await message.answer(
        text=user_messages.ENTER_THE_PHOTO_DEFAULT,
        reply_markup=get_reply_cancel_button(),
    )


@router.message(FSMAddAlbumML.year)
async def add_year_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="текст")
    )


@router.message(FSMAddAlbumML.photo, F.photo)
@router.message(FSMAddAlbumML.photo, F.text)
async def add_photo(message: Message, state: FSMContext):
    """Добавляет фото в FSM."""

    if message.text:
        photo_file_id = None
        photo_file_unique_id = None
    if message.photo:
        photo_file_id: str = message.photo[-1].file_id
        photo_file_unique_id: str = message.photo[-1].file_unique_id

    await state.update_data(photo_file_id=photo_file_id)
    await state.update_data(photo_file_unique_id=photo_file_unique_id)
    await state.set_state(FSMAddAlbumML.songs)

    await message.answer(
        text=user_messages.DROP_THE_SONG,
        reply_markup=get_reply_cancel_button(
            optional_button_text=user_messages.CONFIRMATION_TEXT,
        ),
    )


@router.message(FSMAddAlbumML.songs, F.audio)
@router.message(FSMAddAlbumML.songs, F.voice)
async def add_songs(message: Message, state: FSMContext):
    """Добавляет в FSM сброшенные песни."""

    data: Dict = await state.get_data()
    state_data: AddAlbumData = AddAlbumData(**data)
    if message.audio:
        title: str = message.audio.file_name
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    if message.voice:
        song_counter: int = state_data.song_counter + 1
        title: str = f"Unknown title {song_counter}"
        file_id: str = message.voice.file_id
        file_unique_id: str = message.voice.file_unique_id

        await state.update_data(song_counter=song_counter)

    song: SongResponse = SongResponse(
        title=title,
        file_id=file_id,
        file_unique_id=file_unique_id,
    )
    songs: List[SongResponse] = state_data.songs
    songs.append(song)
    await message.answer(text=user_messages.THE_SONG_IS_SAVED.format(title=title))


@router.message(FSMAddAlbumML.songs, F.text == user_messages.CONFIRMATION_TEXT)
async def confirm_add_songs(message: Message, state: FSMContext):
    """Просит подтвердить добавление песен."""

    data: Dict = await state.get_data()
    state_data: AddAlbumData = AddAlbumData(**data)
    songs: List[SongResponse] = state_data.songs
    if not songs:  # Если песен не было сброшено
        await message.answer(
            text=f"{user_messages.NO_SONGS_WERE_DROPPED}\n\n{user_messages.DROP_THE_SONG}"
        )
        return

    count: int = len(songs)
    await state.set_state(FSMAddAlbumML.processing)
    await message.answer(
        text=user_messages.SONGS_WILL_BE_ADDED_IN_QUANTITY.format(count=count),
    )


@router.message(FSMAddAlbumML.songs)
async def add_songs_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="аудио")
    )


@router.message(FSMAddAlbumML.processing, F.text == user_messages.CONFIRMATION_TEXT)
async def end_add_album(
    message: Message,
    state: FSMContext,
    bot,
):
    """Создает альбом."""

    data: Dict = await state.get_data()
    state_data: AddAlbumData = AddAlbumData(**data)
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    chat_id: int = message.chat.id

    result_add_album = await AddAlbumExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        executor_id=state_data.executor_id,
        title=state_data.title,
        year=state_data.year,
        songs=state_data.songs,
        photo_file_id=state_data.photo_file_id,
        photo_file_unique_id=state_data.photo_file_unique_id,
    )
    if result_add_album.ok:
        await state.clear()
        result_message: str = resolve_message(code=result_add_album.code)
        await return_to_executor_page(
            bot=bot,
            uow=UnitOfWork,
            logging_data=logging_data,
            chat_id=chat_id,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            message=result_message,
            album_position=0,
            mode=LibraryMode(user_id=state_data.user_id),
            limit_albums=LIMIT_ALBUMS,
            current_page_executor=state_data.current_page_executor,
            get_information_executor=get_information_executor,
        )

        return
    if not result_add_album.ok:
        await state.update_data(songs=[])
        await state.set_state(FSMAddAlbumML.title)
        error_message: str = resolve_message(code=result_add_album.error.code)
        await message.answer(
            text=f"{error_message}\n\n{user_messages.ENTER_THE_ALBUM_TITLE}"
        )


@router.message(FSMAddAlbumML.processing)
async def end_add_album_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(
            format=f"{user_messages.CONFIRMATION_TEXT}\n{KeyboardResponse.USER_CANCEL_BUTTON.value}"
        )
    )


# добавление песен в альбом
class FSMAddSongsAlbumML(StatesGroup):
    """FSM для сценария добавления песен в альбом."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    song_counter: State = State()
    songs: State = State()
    processing: State = State()


@dataclass
class AddSongsAlbumMLData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    song_counter: int
    songs: List[SongResponse]
    processing: None


@router.callback_query(StateFilter(None), AddCallbackDataFilters.AddSongsAlbum.filter())
async def start_add_songs_album(
    call: CallbackQuery,
    callback_data: AddCallbackDataFilters.AddSongsAlbum,
    state: FSMContext,
):
    """Просит скинуть песни для добавления в альбома."""

    await call.message.edit_reply_markup(reply_markup=None)

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor

    await state.update_data(
        AddSongsAlbumMLData(
            current_page_executor=current_page_executor,
            executor_id=executor_id,
            user_id=user_id,
            album_id=album_id,
            is_global_executor=is_global_executor,
            songs=[],
            song_counter=0,
            music_library_album=True,
            album_position=album_position,
            processing=None,
        ).__dict__
    )

    await state.set_state(FSMAddSongsAlbumML.songs)

    await call.message.answer(
        text=user_messages.DROP_THE_SONG,
        reply_markup=get_reply_cancel_button(
            optional_button_text=user_messages.CONFIRMATION_TEXT
        ),
    )


@router.message(FSMAddSongsAlbumML.songs, F.audio)
@router.message(FSMAddSongsAlbumML.songs, F.voice)
async def add_songs_album(message: Message, state: State):
    """Добавляет в FSM сброшенные песни."""

    data: Dict = await state.get_data()
    state_data: AddSongsAlbumMLData = AddSongsAlbumMLData(**data)
    if message.audio:
        title: str = message.audio.file_name
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    if message.voice:
        song_counter: int = state_data.song_counter + 1
        title: str = f"Unknown title {song_counter}"
        file_id: str = message.voice.file_id
        file_unique_id: str = message.voice.file_unique_id

        await state.update_data(song_counter=song_counter)

    song: SongResponse = SongResponse(
        title=title,
        file_id=file_id,
        file_unique_id=file_unique_id,
    )
    songs: List[SongResponse] = state_data.songs
    songs.append(song)
    await message.answer(text=user_messages.THE_SONG_IS_SAVED.format(title=title))


@router.message(FSMAddSongsAlbumML.songs, F.text == user_messages.CONFIRMATION_TEXT)
async def confirm_add_songs_album(message: Message, state: FSMContext):
    """Просит подтвердить добавление песен."""

    data: Dict = await state.get_data()
    state_data: AddSongsAlbumMLData = AddSongsAlbumMLData(**data)
    songs: List[SongResponse] = state_data.songs
    if not songs:  # Если песен не было сброшено
        await message.answer(
            text=f"{user_messages.NO_SONGS_WERE_DROPPED}\n\n{user_messages.DROP_THE_SONG}"
        )
        return

    count: int = len(songs)
    await state.set_state(FSMAddSongsAlbumML.processing)
    await message.answer(
        text=user_messages.SONGS_WILL_BE_ADDED_IN_QUANTITY.format(count=count),
    )


@router.message(FSMAddSongsAlbumML.songs)
async def add_songs_album_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="аудио")
    )

    await message.answer(text=user_messages.DROP_THE_SONG)


@router.message(
    FSMAddSongsAlbumML.processing, F.text == user_messages.CONFIRMATION_TEXT
)
async def end_songs_album(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    data: Dict = await state.get_data()
    state_data: AddSongsAlbumMLData = AddSongsAlbumMLData(**data)
    chat_id: int = message.chat.id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await AddSongsAlbum(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        executor_id=state_data.executor_id,
        album_id=state_data.album_id,
        songs=state_data.songs,
    )

    await state.clear()
    if result.ok:
        result_message: str = resolve_message(code=result.code)
        await return_to_album_page(
            chat_id=chat_id,
            bot=bot,
            message=result_message,
            logging_data=logging_data,
            uow=UnitOfWork,
            current_page_executor=state_data.current_page_executor,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            limit_songs=LIMIT_SONGS,
            get_information_album=get_information_album,
            album_id=state_data.album_id,
            executor_id=state_data.executor_id,
            song_position=0,
            is_global_executor=state_data.is_global_executor,
            album_position=state_data.album_position,
            user_id=state_data.user_id,
        )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)

        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


@router.message(FSMAddSongsAlbumML.processing)
async def end_songs_album_message(message: Message):
    """Отправляет сообщение если были введены данные не в том формате."""

    await message.answer(
        text=user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(
            format=user_messages.CONFIRMATION_TEXT
        )
    )
    await message.answer(text=user_messages.CLICK_CANCEL_BUTTON)
