from dataclasses import dataclass
from typing import List, Dict, Set

from aiogram import Router
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters.state import StateFilter

from app.bot.modules.music_library.childes.collection_of_songs.settings import settings
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from app.bot.modules.music_library.services.collection_songs import (
    callback_show_user_collection,
)
from app.bot.modules.main.settings import settings as main_settings
from application.use_cases.db.collection_songs.get_user_collection_songs import (
    GetUserCollectionSongs,
)
from application.use_cases.db.collection_songs.delete_songs_collection_songs import (
    DeleteSongsCollectionSongs,
)
from domain.entities.db.models.user import User as UserDomain
from domain.entities.response import (
    CollectionSongsResponse,
    UserCollectionSongsResponse,
)
from infrastructure.db.uow import UnitOfWork
from infrastructure.aiogram.keyboards.inline import (
    get_menu_songs_collection_songs_delete,
    get_confirmation_delete_song_button,
)
from infrastructure.aiogram.filters import (
    DeleteCallbackDataFilters,
    ScrollingCallbackDataFilters,
)
from infrastructure.aiogram.messages import LIMIT_COLLECTION_SONGS, resolve_message
from infrastructure.aiogram.messages import user_messages
from core.logging.api import get_loggers
from core.response.response_data import LoggingData, Result


router: Router = Router(name=__name__)


# Удаление песен альбома
class FSMDeleteSongsCollectionSongs(StatesGroup):
    """FSM для сценария удаления песен из сборника."""

    collection_songs: State = State()
    state_data: State = State()


@dataclass
class SongsDeleteCollectionSongs:
    """Хранит данные для удаления песен."""

    songs: List[CollectionSongsResponse]
    selected_songs_ids: List[int]


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.SongCollectionSongs.filter()
)
async def start_delete_songs_collection_songs(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.SongCollectionSongs,
    state: FSMContext,
    user: UserDomain,
):
    """Просит выбрать песню для удаления."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result: Result = await GetUserCollectionSongs(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user=user)
    if result.ok:
        user_resonse: UserCollectionSongsResponse = result.data

        collection_songs = user_resonse.collection_songs

        await state.update_data(
            state_data=SongsDeleteCollectionSongs(
                songs=collection_songs,
                selected_songs_ids=set(),
            )
        )

        len_list_songs: int = len(collection_songs)

        collection_songs: List[CollectionSongsResponse] = collection_songs[
            0:LIMIT_COLLECTION_SONGS
        ]

        await state.update_data(collection_songs=True)
        await state.set_state(FSMDeleteSongsCollectionSongs.state_data)
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
            ),
            reply_markup=get_menu_songs_collection_songs_delete(
                len_list_songs=len_list_songs,
                limit_songs=LIMIT_COLLECTION_SONGS,
                song_position=0,
                list_songs=collection_songs,
                delete_songs=set(),
            ),
        ),
    if not result.ok:
        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MY_MUSIC_COLLECTION,
            message=result.error.message,
        )


@router.callback_query(
    FSMDeleteSongsCollectionSongs.state_data,
    DeleteCallbackDataFilters.ButtonsDeleteSongColletionSongs.filter(),
)
async def delete_songs_buttons(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ButtonsDeleteSongColletionSongs.filter(),
    state: FSMContext,
):
    """Отмечает выбранную песню как готовую к удалению или снимает с удаления."""

    data: Dict = await state.get_data()
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    songs: List[CollectionSongsResponse] = data["state_data"].songs
    len_list_songs: int = len(songs)  # получаем общее количество песен до изменения

    song_id: int = callback_data.song_id
    position: int = callback_data.position

    songs = songs[
        position : position + LIMIT_COLLECTION_SONGS
    ]  # измененяем песни с учетом позиции
    if song_id in delete_songs:  # если песня уже есть на удаление- убирает ее
        delete_songs.remove(song_id)
    else:  # если песни нету на удаление - добавляем ее
        delete_songs.add(song_id)

    data["state_data"].selected_songs_ids = list(delete_songs)  # сохраняем списком

    await state.update_data(state_data=data["state_data"])  # обновляем состояние

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=main_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
        ),
        reply_markup=get_menu_songs_collection_songs_delete(
            list_songs=songs,
            song_position=position,
            len_list_songs=len_list_songs,
            limit_songs=LIMIT_COLLECTION_SONGS,
            delete_songs=delete_songs,
        ),
    ),


@router.callback_query(
    FSMDeleteSongsCollectionSongs.state_data,
    ScrollingCallbackDataFilters.DeleteMenuSongColletionSongs.filter(),
)
async def scrolling_songe_menu_delete(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.DeleteMenuSongColletionSongs,
    state: FSMContext,
    user: UserDomain,
):
    """Пролистывает песни из меню удаления песен."""

    data: Dict = await state.get_data()

    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    position: int = callback_data.position + callback_data.offset
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    result_scrolling = await GetUserCollectionSongs(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user=user)
    if result_scrolling.ok:
        user_resonse: UserCollectionSongsResponse = result_scrolling.data

        songs: List[CollectionSongsResponse] = user_resonse.collection_songs
        len_list_songs: int = len(songs)

        songs = songs[position : position + LIMIT_COLLECTION_SONGS]

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
            ),
            reply_markup=get_menu_songs_collection_songs_delete(
                len_list_songs=len_list_songs,
                limit_songs=LIMIT_COLLECTION_SONGS,
                delete_songs=delete_songs,
                song_position=position,
                list_songs=songs,
            ),
        )
    if not result_scrolling.ok:
        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MY_MUSIC_COLLECTION,
            message=result_scrolling.error.message,
        )


@router.callback_query(
    FSMDeleteSongsCollectionSongs.state_data,
    DeleteCallbackDataFilters.ConfirmDeleteSongCollectionSongs.filter(),
)
async def confirm_delete_songs(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ConfirmDeleteSongCollectionSongs,
    state: FSMContext,
) -> None:
    """Подтверждение на удаление песен."""

    data: Dict = await state.get_data()

    delete_songs: Set = data["state_data"].selected_songs_ids

    if delete_songs:  # если были выбраны песни
        count: int = len(delete_songs)
        collection_songs = data["state_data"].songs
        positions = []
        for song in collection_songs:
            if song.id in delete_songs:
                positions.append(song.position)
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=user_messages.MESSAGE_TO_CONFIRM_THE_DELETION_OF_SONGS.format(
                    count=count, positions=str(positions)
                ),
            ),
            reply_markup=get_confirmation_delete_song_button(),
        )
        return

    # Если не было выбрано песен, просит выбрать песни
    await call.message.answer(text=user_messages.SELECT_THE_SONGS_TO_DELETE)


@router.callback_query(
    FSMDeleteSongsCollectionSongs.state_data,
    DeleteCallbackDataFilters.CompleteDeleteSongCollectionSongs.filter(),
)
async def delete_collection_songs(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.CompleteDeleteSongCollectionSongs,
    state: FSMContext,
    user: UserDomain,
):
    """Удаляет песни."""
    data: Dict = await state.get_data()
    user_response: SongsDeleteCollectionSongs = data["state_data"]
    selected_songs_ids = user_response.selected_songs_ids
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_delete = await DeleteSongsCollectionSongs(
        uow=UnitOfWork(),
        logging_data=logging_data,
    ).execute(user_id=user.id, list_ids=selected_songs_ids)

    await state.clear()
    if result_delete.ok:
        msg_result_delete = resolve_message(code=result_delete.code)

        result = await GetUserCollectionSongs(
            uow=UnitOfWork(), logging_data=logging_data
        ).execute(
            user=user,
        )
        if result.ok:
            user_response = result.data
            await callback_show_user_collection(
                call=call,
                user_response=user_response,
                caption=user_messages.MY_COLLECTION_OF_SONGS,
                limit_collection_songs=LIMIT_COLLECTION_SONGS,
                start_collection_songs=0,
                message=msg_result_delete,
            )
    if not result_delete.ok:
        error_message: str = resolve_message(code=result_delete.error.code)
        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.MY_MUSIC_COLLECTION,
            message=error_message,
        )


@router.message(FSMDeleteSongsCollectionSongs.state_data)
async def delete_collection_songs_message(message: Message):
    """Отправляет сообщение при вводе любых данных"""
    await message.answer(text=user_messages.CLICK_ONE_OF_THE_BUTTONS_ABOVE)
