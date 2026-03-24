from dataclasses import dataclass
from typing import Optional, List, Dict

from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.settings import settings as bot_settings
from app.bot.helpers.executor import return_to_executor_page
from application.use_cases.db.music_library.add_album import AddAlbumExecutor
from domain.entities.response import SongResponse
from infrastructure.aiogram.filters import AddCallbackDataFilters
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.aiogram.messages import user_messages, LIMIT_ALBUMS, resolve_message
from infrastructure.aiogram.response import KeyboardResponse
from infrastructure.db.uow import UnitOfWork
from infrastructure.db.utils.editing import get_information_executor
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
class UserAddAlbumProtocol:
    current_page_executor: int = None
    music_library_executor: bool = None
    song_counter: Optional[int] = None
    executor_id: int = None
    user_id: Optional[int] = None
    title: str = None
    year: int = None
    photo_file_id: Optional[str] = None
    photo_file_unique_id: Optional[str] = None
    songs: List[SongResponse] = None
    photo: None = None
    processing: None = None


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

    await state.update_data(executor_id=executor_id)
    await state.update_data(user_id=user_id)
    await state.update_data(song_counter=0)
    await state.update_data(current_page_executor=current_page_executor)
    await state.update_data(music_library_executor=True)
    await state.update_data(songs=[])
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
    add_album_data: UserAddAlbumProtocol = UserAddAlbumProtocol(**data)
    if message.audio:
        title: str = message.audio.file_name
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    if message.voice:
        song_counter: int = add_album_data.song_counter + 1
        title: str = f"Unknown title {song_counter}"
        file_id: str = message.voice.file_id
        file_unique_id: str = message.voice.file_unique_id

        await state.update_data(song_counter=song_counter)

    song: SongResponse = SongResponse(
        title=title,
        file_id=file_id,
        file_unique_id=file_unique_id,
    )
    songs: List[SongResponse] = add_album_data.songs
    songs.append(song)
    await message.answer(text=user_messages.THE_SONG_IS_SAVED.format(title=title))


@router.message(FSMAddAlbumML.songs, F.text == user_messages.CONFIRMATION_TEXT)
async def confirm_add_songs(message: Message, state: FSMContext):
    """Просит подтвердить добавление песен."""

    data: Dict = await state.get_data()
    add_album_data: UserAddAlbumProtocol = UserAddAlbumProtocol(**data)
    songs: List[SongResponse] = add_album_data.songs
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
    add_album_data: UserAddAlbumProtocol = UserAddAlbumProtocol(**data)
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )
    chat_id: int = message.chat.id

    result_add_album = await AddAlbumExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        executor_id=add_album_data.executor_id,
        title=add_album_data.title,
        year=add_album_data.year,
        songs=add_album_data.songs,
        photo_file_id=add_album_data.photo_file_id,
        photo_file_unique_id=add_album_data.photo_file_unique_id,
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
            user_id=add_album_data.user_id,
            limit_albums=LIMIT_ALBUMS,
            current_page_executor=add_album_data.current_page_executor,
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
