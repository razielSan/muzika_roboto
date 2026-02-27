from typing import Dict, List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from infrastructure.aiogram.filters import AddCallbackDataFilters
from infrastructure.aiogram.messages import user_messages
from core.response.messages import messages
from domain.entities.response import CollectionSongResponse
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from core.response.messages import messages
from app.bot.utils.delete import delete_previous_message
from application.use_cases.db.add_songs_to_collection_songs import (
    AddSongsToCollectionSong,
)
from application.use_cases.db.get_user_collection_song import GetUserCollectionSong
from infrastructure.db.uow import UnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode
from infrastructure.aiogram.messages import ERRORS, LIMIT_COLLECTION_SONG, NOT_FOUND
from core.logging.api import get_loggers
from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.settings import settings as music_libarary_settings
from infrastructure.aiogram.keyboards.inline import get_buttons_for_song_collection_user
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.modules.music_library.utils.music_library import show_user_collection
from core.response.response_data import Result, LoggingData

router: Router = Router(name=__name__)


class FSMAddSongCollection(StatesGroup):
    unique_songs_titles: State = State()
    counter: State = State()
    songs: State = State()
    processing: State = State()


@router.callback_query(
    StateFilter(None), AddCallbackDataFilters.CollectionSong.filter()
)
async def start_add_collection_song(
    call: CallbackQuery,
    callback_data: AddCallbackDataFilters.CollectionSong,
    state: FSMContext,
):
    """Просит пользователю скнуть песни."""

    await call.message.edit_reply_markup(reply_markup=None)

    await call.message.answer(
        text=f"{user_messages.DROP_THE_SONG}",
        reply_markup=get_reply_cancel_button(
            optional_button_text=user_messages.CONFIRMATION_TEXT,
        ),
    )

    await state.update_data(unique_songs_titles=[])
    await state.update_data(songs=[])
    await state.update_data(counter=0)
    await state.set_state(FSMAddSongCollection.songs)


@router.message(
    FSMAddSongCollection.processing, F.text == user_messages.USER_CANCEL_TEXT
)
@router.message(FSMAddSongCollection.songs, F.text == user_messages.USER_CANCEL_TEXT)
async def cancel_handler(message: Message, bot: Bot, state: FSMContext):
    """Отменяет все запросы."""

    telegram: int = message.chat.id
    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result: Result = await GetUserCollectionSong(
        logging_data=logging_data,
        uow=UnitOfWork(),
    ).execute(telegram=telegram)

    await state.clear()
    if result.ok and not result.empty:
        await show_user_collection(
            user_response=result.data,
            start_collection_song=0,
            limit_collection_song=LIMIT_COLLECTION_SONG,
            bot=bot,
            chat_id=telegram,
            caption=user_messages.MY_COLLECTION_OF_SONGS,
            photo_file_id=music_libarary_settings.COLLECTION_SONG_PHOTO_FILE_ID,
            message=user_messages.USER_CANCEL_MESSAGE,
        )


@router.message(FSMAddSongCollection.songs, F.audio)
@router.message(FSMAddSongCollection.songs, F.voice)
async def add_songs(
    message: Message,
    state: State,
):
    """Добавляет песни в список для сохранения."""

    data: Dict = await state.get_data()
    counter: int = data.get("counter", 0)
    if message.voice:
        counter += 1
        title = f"{messages.UNKNOWN_TITLE_TEXT} {counter}"
        file_id: str = message.voice.file_id
        file_unique_id: str = message.voice.file_unique_id
        await state.update_data(counter=counter)

    if message.audio:
        title: str = message.audio.file_name.split(".")[0].strip()
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    unique_songs_titles: List[str] = data["unique_songs_titles"]
    songs: List[CollectionSongResponse] = data["songs"]
    if title in unique_songs_titles:  # Если песня с таким названием уже была добавлена
        await message.answer(
            text=user_messages.THE_SONG_HAS_ALREADY_BEEN_ADDED.format(title=title),
        )
    else:
        songs.append(
            CollectionSongResponse(
                file_id=file_id, file_unique_id=file_unique_id, title=title
            ),
        )
        await message.answer(
            text=user_messages.THE_SONG_IS_SAVED.format(title=title),
        )
        unique_songs_titles.append(title)
        await state.update_data(songs=songs)
        await state.update_data(unique_songs_titles=unique_songs_titles)


@router.message(FSMAddSongCollection.songs, F.text == user_messages.CONFIRMATION_TEXT)
async def confirm_add_songs_collection(message: Message, state: State, bot: Bot):
    """Просит пользователя подтвердить добавление песен."""

    data: Dict = await state.get_data()

    songs: List[CollectionSongResponse] = data["songs"]
    if len(songs) == 0:  # если не было добавлено песен
        await message.answer(
            f"{user_messages.NO_SONGS_WERE_DROPPED}\n\n"
            f"{user_messages.DROP_THE_SONG}\n"
        )
        return

    count_songs: int = len(songs)
    await state.set_state(FSMAddSongCollection.processing)
    await message.answer(
        text=user_messages.SONGS_WILL_BE_ADDED_IN_QUANTITY.format(count=count_songs)
    )


@router.message(FSMAddSongCollection.songs, F.text)
async def add_songs_collection_message(
    message: Message,
    bot: Bot,
):
    """Отправляет сообщение при отправе данных не в нужном формате."""

    await delete_previous_message(bot=bot, message=message)

    msg: str = user_messages.THE_DATA_MUST_BE_IN_THE_FORMAT.format(format="аудио")

    await message.answer(
        text=f"{msg}\n\n{user_messages.DROP_THE_SONG}",
        reply_markup=get_reply_cancel_button(
            optional_button_text=user_messages.CONFIRMATION_TEXT
        ),
    )


@router.message(
    FSMAddSongCollection.processing, F.text == user_messages.CONFIRMATION_TEXT
)
async def final_add_collection_songs(
    message: Message,
    state: FSMContext,
    bot: Bot,
):
    """Сохраняет песни в сборник песен."""

    data: Dict = await state.get_data()
    songs: List[CollectionSongResponse] = data.get("songs")

    telegram: int = message.from_user.id
    name: str = message.from_user.first_name

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_add_song: Result = await AddSongsToCollectionSong(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user_name=name, telegram=telegram, collection_songs=songs)

    await state.clear()
    if result_add_song.ok:
        result: Result = await GetUserCollectionSong(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(telegram=telegram)

        if result.ok and not result.empty:
            await show_user_collection(
                user_response=result.data,
                start_collection_song=0,
                limit_collection_song=LIMIT_COLLECTION_SONG,
                bot=bot,
                chat_id=telegram,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                photo_file_id=music_libarary_settings.COLLECTION_SONG_PHOTO_FILE_ID,
                message=user_messages.SONGS_ADDED_SUCCESSSFULLY,
            )
            return

        if not result.ok:
            error_message = None
            if result.error.code == ErorrCode.UNKNOWN_ERROR.name:
                error_message: str = ERRORS[result.error.code]

            if result.error.code == NotFoundCode.USER_NOT_FOUND.name:
                error_message: str = NOT_FOUND[result.error.code]
            await get_inline_menu_music_library(
                chat_id=telegram,
                bot=bot,
                message=error_message,
            )
            return

    if not result_add_song.ok:
        if result_add_song.error.code == ErorrCode.UNKNOWN_ERROR.name:
            error_message = ERRORS[result.error.code]
            await get_inline_menu_music_library(
                chat_id=telegram,
                bot=bot,
                message=error_message,
            )


@router.message(FSMAddSongCollection.processing, F.text)
async def final_add_collection_song(
    message: Message,
    bot: Bot,
):
    """Отправляет сообщение при отправе данных не в нужном формате."""

    await delete_previous_message(
        bot=bot,
        message=message,
    )

    await message.answer(
        text=user_messages.PRESS_ONE_OF_THE_BUTTONS,
        reply_markup=get_reply_cancel_button(
            optional_button_text=user_messages.CONFIRMATION_TEXT
        ),
    )
