from typing import Dict, List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.utils.music_library import (
    get_inline_menu_music_library,
)
from app.bot.modules.music_library.services.collection_songs import show_user_collection
from app.bot.utils.delete import delete_previous_message
from application.use_cases.db.collection_songs.add_songs_to_collection_songs import (
    AddSongsToCollectionSongs,
)
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from domain.entities.response import CollectionSongsResponse
from infrastructure.aiogram.filters import AddCallbackDataFilters
from infrastructure.aiogram.messages import user_messages
from infrastructure.aiogram.keyboards.reply import get_reply_cancel_button
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.messages import (
    LIMIT_COLLECTION_SONGS,
    resolve_message,
)
from core.response.messages import messages
from core.logging.api import get_loggers
from core.response.response_data import Result, LoggingData


router: Router = Router(name=__name__)


class FSMAddSongCollection(StatesGroup):
    """FSM для сценария добавления песен в сборник."""

    collection_songs: State = State()  # Для возврата к сборнику песен при отмене
    unique_songs_titles: State = State()
    counter: State = State()
    songs: State = State()
    processing: State = State()


@router.callback_query(
    StateFilter(None), AddCallbackDataFilters.SongCollectionSongs.filter()
)
async def start_add_collection_song(
    call: CallbackQuery,
    callback_data: AddCallbackDataFilters.SongCollectionSongs,
    state: FSMContext,
):
    """Просит пользователю скинуть песни."""

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
    await state.update_data(collection_songs=True)
    await state.set_state(FSMAddSongCollection.songs)


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
        title: str = message.audio.file_name.lower()
        file_id: str = message.audio.file_id
        file_unique_id: str = message.audio.file_unique_id

    unique_songs_titles: List[str] = data["unique_songs_titles"]
    songs: List[CollectionSongsResponse] = data["songs"]
    if title in unique_songs_titles:  # Если песня с таким названием уже была добавлена
        await message.answer(
            text=user_messages.THE_SONG_HAS_ALREADY_BEEN_ADDED.format(title=title),
        )
    else:
        songs.append(
            CollectionSongsResponse(
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

    songs: List[CollectionSongsResponse] = data["songs"]
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
    user,
):
    """Сохраняет песни в сборник песен."""

    data: Dict = await state.get_data()
    songs: List[CollectionSongsResponse] = data.get("songs")

    chat_id: int = message.chat.id
    name: str = message.from_user.first_name

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_add_song: Result = await AddSongsToCollectionSongs(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(collection_songs=songs, user_id=user.id)

    await state.clear()
    if result_add_song.ok:
        msg_add_song: str = resolve_message(code=result_add_song.code)
        result: Result = await GetUserCollectionSongs(
            logging_data=logging_data,
            uow=UnitOfWork(),
        ).execute(user=user)

        if result.ok:
            await show_user_collection(
                user_response=result.data,
                start_collection_songs=0,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                bot=bot,
                chat_id=chat_id,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                message=msg_add_song,
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
            return

    if not result_add_song.ok:
        error_message: str = resolve_message(code=result_add_song.error.code)
        await get_inline_menu_music_library(
            chat_id=chat_id,
            bot=bot,
            message=error_message,
            caption=user_messages.MAIN_MENU,
        )


@router.message(FSMAddSongCollection.processing)
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
