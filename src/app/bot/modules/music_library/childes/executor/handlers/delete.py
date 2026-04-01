from typing import Optional, List, Dict, Set
from dataclasses import dataclass

from aiogram import Router
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.bot.settings import settings as bot_settings
from app.bot.modules.music_library.settings import settings as music_library_settings
from app.bot.helpers.executor import return_to_executor_page_callback
from app.bot.helpers.album import return_to_album_page_callback
from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
)
from application.use_cases.db.music_library.delete.delete_executor import DeleteExecutor
from application.use_cases.db.music_library.get.get_album_with_songs import (
    GetAlbumWithSongs,
)
from application.use_cases.db.music_library.delete.delete_songs import DeleteSongsAlbum
from application.use_cases.db.music_library.delete.delete_album import DeleteAlbum
from domain.entities.response import SongResponse, AlbumPageResponse, LibraryMode
from infrastructure.aiogram.filters import DeleteCallbackDataFilters
from infrastructure.aiogram.messages import (
    user_messages,
    LIMIT_ALBUMS,
    resolve_message,
    LIMIT_SONGS,
)
from infrastructure.aiogram.filters import (
    DeleteCallbackDataFilters,
    ScrollingCallbackDataFilters,
)
from infrastructure.db.utils.editing import (
    get_information_executor,
    get_information_album,
)
from infrastructure.aiogram.keyboards.inline import (
    get_confirmation_delete_executor_button,
    get_confirmation_delete_album_buttons,
    get_confirmation_delete_album_songs_button,
    get_menu_album_songs_delete,
)
from infrastructure.db.uow import UnitOfWork
from core.logging.api import get_loggers
from core.response.response_data import Result, LoggingData

router: Router = Router(name=__name__)


# удаление исполнителя
@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.ConfirmDeleteExecutor.filter()
)
async def delete_user_executor(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ConfirmDeleteExecutor,
):
    """Просит подтвердить удаление исполнителя."""

    user_id: int = callback_data.user_id
    executor_id: int = callback_data.executor_id
    current_page_executor: int = callback_data.current_page_executor
    album_position: int = callback_data.album_position

    await call.message.edit_media(
        InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.CAPTION_DELETE_EXECUTOR,
        ),
        reply_markup=get_confirmation_delete_executor_button(
            executor_id=executor_id,
            user_id=user_id,
            current_page_executor=current_page_executor,
            album_position=album_position,
        ),
    )


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.CompleteDeleteExecutor.filter()
)
async def confirm_delete_executor(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.CompleteDeleteExecutor,
):
    """Удаляет исполнителя."""

    executor_id: Optional[int] = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result_delete_executor: Result = await DeleteExecutor(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(user_id=user_id, executor_id=executor_id)
    if result_delete_executor.ok:
        result_message: str = resolve_message(code=result_delete_executor.code)

        await return_to_executor_page_callback(
            mode=LibraryMode(user_id=user_id),
            uow=UnitOfWork,
            call=call,
            message=result_message,
            logging_data=logging_data,
            current_page_executor=1,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            get_information_executor=get_information_executor,
        )

    if not result_delete_executor.ok:
        error_message: str = resolve_message(code=result_delete_executor.error.code)

        await callback_update_menu_inline_music_library(
            call=call,
            caption=user_messages.USER_PANEL_CAPTION,
            message=error_message,
        )


# удаление альбома


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.ConfirmDeleteAlbum.filter()
)
async def start_delete_album(
    call: CallbackQuery, callback_data: DeleteCallbackDataFilters.ConfirmDeleteAlbum
):
    """Просит подтвердить удаления альбома."""

    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor
    is_global_executor: bool = callback_data.is_global_executor
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position

    await call.message.edit_media(
        InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.CAPTION_DELETE_ALBUM,
        ),
        reply_markup=get_confirmation_delete_album_buttons(
            executor_id=executor_id,
            user_id=user_id,
            current_page_executor=current_page_executor,
            is_global_executor=is_global_executor,
            album_id=album_id,
            album_position=album_position,
        ),
    )


@router.callback_query(
    StateFilter(None), DeleteCallbackDataFilters.CompleteDeleteAlbum.filter()
)
async def end_delete_album(
    call: CallbackQuery, callback_data: DeleteCallbackDataFilters.CompleteDeleteAlbum
):
    """удаляет альбом."""

    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    current_page_executor: int = callback_data.current_page_executor
    album_id: int = callback_data.album_id
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result_delete_album: Result = await DeleteAlbum(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(executor_id=executor_id, album_id=album_id)
    if result_delete_album.ok:
        result_message: str = resolve_message(code=result_delete_album.code)

        await return_to_executor_page_callback(
            mode=LibraryMode(user_id=user_id),
            uow=UnitOfWork,
            call=call,
            message=result_message,
            logging_data=logging_data,
            current_page_executor=current_page_executor,
            executor_default_photo_file_id=bot_settings.EXECUTOR_DEFAULT_PHOTO_FILE_ID,
            limit_albums=LIMIT_ALBUMS,
            album_position=0,
            get_information_executor=get_information_executor,
        )

    if not result_delete_album.ok:
        error_message: str = resolve_message(code=result_delete_album.error.code)

        await callback_update_menu_inline_music_library(
            call=call,
            message=error_message,
            caption=user_messages.USER_PANEL_CAPTION,
        )


# удаление песен альбома


@dataclass
class SongsStorage:
    """Хранит данные для удаления песен."""

    songs: List[SongResponse]
    selected_songs_ids: Set[int]


class FSMDeleteSongsAlbumML(StatesGroup):
    """FSM для сценария удаления песен из альбома."""

    current_page_executor: State = State()
    music_library_album: State = State()
    executor_id: State = State()
    user_id: State = State()
    album_id: State = State()
    is_global_executor: State = State()
    album_position: State = State()
    year: State = State()
    state_data: State = State()


@dataclass
class DeleteSongsAlbumData:
    current_page_executor: int
    music_library_album: bool
    executor_id: int
    user_id: Optional[int]
    album_id: int
    is_global_executor: bool
    album_position: int
    state_data: SongsStorage


@router.callback_query(StateFilter(None), DeleteCallbackDataFilters.SongsAlbum.filter())
async def start_delete_songs_collection_songs(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.SongsAlbum,
    state: FSMContext,
):
    """Просит выбрать песни альбома для удаления."""

    current_page_executor: int = callback_data.current_page_executor
    executor_id: int = callback_data.executor_id
    user_id: Optional[int] = callback_data.user_id
    album_id: int = callback_data.album_id
    album_position: int = callback_data.album_position
    is_global_executor: bool = callback_data.is_global_executor

    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await GetAlbumWithSongs(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        user_id=user_id,
        executor_id=executor_id,
        album_id=album_id,
        album_position=album_position,
        current_page_executor=current_page_executor,
        is_global_executor=is_global_executor,
    )
    if result.ok:
        album_response: AlbumPageResponse = result.data

        album_songs: List[SongResponse] = album_response.songs

        await state.update_data(
            DeleteSongsAlbumData(
                current_page_executor=current_page_executor,
                state_data=SongsStorage(
                    songs=album_songs,
                    selected_songs_ids=set(),
                ),
                music_library_album=True,
                executor_id=executor_id,
                user_id=user_id,
                album_id=album_id,
                is_global_executor=is_global_executor,
                album_position=album_position,
            ).__dict__
        )

        len_list_songs: int = len(album_songs)

        album_songs: List[SongResponse] = album_songs[0:LIMIT_SONGS]

        await state.set_state(FSMDeleteSongsAlbumML.state_data)
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=bot_settings.DELETE_IMAGE_FILE_ID,
                caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
            ),
            reply_markup=get_menu_album_songs_delete(
                user_id=user_id,
                album_id=album_id,
                executor_id=executor_id,
                album_position=album_position,
                is_global_executor=is_global_executor,
                current_page_executor=current_page_executor,
                songs=album_songs,
                song_position=0,
                len_list_songs=len_list_songs,
                limit_songs=LIMIT_SONGS,
                delete_songs=set(),
            ),
        ),

    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)

        await callback_update_menu_inline_music_library(
            call=call,
            message=error_message,
            caption=user_messages.USER_PANEL_CAPTION,
        )


@router.callback_query(
    FSMDeleteSongsAlbumML.state_data,
    DeleteCallbackDataFilters.ButtonsDeleteSongAlbum.filter(),
)
async def tag_songs(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ButtonsDeleteSongAlbum,
    state: FSMContext,
):
    """Помечает песни альбома как готовые на удаление."""

    song_id: int = callback_data.song_id
    position: int = callback_data.position

    data: Dict = await state.get_data()
    delete_state_data: DeleteSongsAlbumData = DeleteSongsAlbumData(**data)
    album_songs: List[SongResponse] = delete_state_data.state_data.songs
    len_list_songs: int = len(album_songs)

    # Отправляет в множество id песен для удаления
    del_song_ids = delete_state_data.state_data.selected_songs_ids
    if song_id in del_song_ids:
        del_song_ids.remove(song_id)
    else:
        del_song_ids.add(song_id)

    album_songs = album_songs[position : position + LIMIT_SONGS]

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
        ),
        reply_markup=get_menu_album_songs_delete(
            user_id=delete_state_data.user_id,
            album_id=delete_state_data.album_id,
            executor_id=delete_state_data.executor_id,
            album_position=delete_state_data.album_position,
            is_global_executor=delete_state_data.is_global_executor,
            current_page_executor=delete_state_data.current_page_executor,
            songs=album_songs,
            song_position=position,
            len_list_songs=len_list_songs,
            limit_songs=LIMIT_SONGS,
            delete_songs=del_song_ids,
        ),
    ),


@router.callback_query(
    FSMDeleteSongsAlbumML.state_data,
    ScrollingCallbackDataFilters.DeleteMenuSongAlbum.filter(),
)
async def scrolling_delete_menu_song_album(
    call: CallbackQuery,
    callback_data: ScrollingCallbackDataFilters.DeleteMenuSongAlbum,
    state: FSMContext,
):
    """Листает песни альбома в меню удаления."""

    position: int = callback_data.position
    offset: int = callback_data.offset
    position: int = position + offset

    data: Dict = await state.get_data()
    delete_state_data: DeleteSongsAlbumData = DeleteSongsAlbumData(**data)
    album_songs: List[SongsStorage] = delete_state_data.state_data.songs
    len_list_songs: int = len(album_songs)
    album_songs = album_songs[position : position + LIMIT_SONGS]

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=bot_settings.DELETE_IMAGE_FILE_ID,
            caption=user_messages.SELECT_THE_SONGS_TO_DELETE,
        ),
        reply_markup=get_menu_album_songs_delete(
            user_id=delete_state_data.user_id,
            album_id=delete_state_data.album_id,
            executor_id=delete_state_data.executor_id,
            album_position=delete_state_data.album_position,
            is_global_executor=delete_state_data.is_global_executor,
            current_page_executor=delete_state_data.current_page_executor,
            songs=album_songs,
            song_position=position,
            len_list_songs=len_list_songs,
            limit_songs=LIMIT_SONGS,
            delete_songs=delete_state_data.state_data.selected_songs_ids,
        ),
    ),


@router.callback_query(
    FSMDeleteSongsAlbumML.state_data,
    DeleteCallbackDataFilters.ConfirmDeleteSongAlbum.filter(),
)
async def confirm_delete_song_album(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.ConfirmDeleteSongAlbum,
    state: FSMContext,
):
    """Подтверждение удаление песен альбома."""

    data: Dict = await state.get_data()
    delete_state_data: DeleteSongsAlbumData = DeleteSongsAlbumData(**data)
    del_songs_ids: Set[int] = delete_state_data.state_data.selected_songs_ids
    songs: List[SongResponse] = delete_state_data.state_data.songs
    positions: List[int] = []
    for song in songs:
        if song.id in del_songs_ids:
            positions.append(song.position)
    if positions:
        count: int = len(positions)

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=bot_settings.DELETE_IMAGE_FILE_ID,
                caption=user_messages.MESSAGE_TO_CONFIRM_THE_DELETION_OF_SONGS.format(
                    count=count,
                    positions=str(
                        positions,
                    ),
                ),
            ),
            reply_markup=get_confirmation_delete_album_songs_button(
                executor_id=delete_state_data.executor_id,
                user_id=delete_state_data.user_id,
                current_page_executor=delete_state_data.current_page_executor,
                is_global_executor=delete_state_data.is_global_executor,
                album_id=delete_state_data.album_id,
                album_position=delete_state_data.album_position,
            ),
        )
    if not positions:
        await call.answer(text=user_messages.SELECT_THE_SONGS_TO_DELETE)


@router.callback_query(
    FSMDeleteSongsAlbumML.state_data,
    DeleteCallbackDataFilters.CompleteDeleteSongAlbum.filter(),
)
async def end_delete_songs_album(
    call: CallbackQuery,
    callback_data: DeleteCallbackDataFilters.CompleteDeleteSongAlbum,
    state: FSMContext,
):
    """Удаление песен альбома."""

    data: Dict = await state.get_data()
    delete_state_data: DeleteSongsAlbumData = DeleteSongsAlbumData(**data)
    logging_data: LoggingData = get_loggers(
        name=music_library_settings.NAME_FOR_LOG_FOLDER
    )

    result: Result = await DeleteSongsAlbum(
        uow=UnitOfWork(), logging_data=logging_data
    ).execute(
        album_id=delete_state_data.album_id,
        songs_id=delete_state_data.state_data.selected_songs_ids,
    )
    await state.clear()
    if result.ok:
        result_message: str = resolve_message(code=result.code)
        await return_to_album_page_callback(
            call=call,
            uow=UnitOfWork,
            logging_data=logging_data,
            current_page_executor=delete_state_data.current_page_executor,
            album_default_photo_file_id=bot_settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
            limit_songs=LIMIT_SONGS,
            get_information_album=get_information_album,
            album_id=delete_state_data.album_id,
            executor_id=delete_state_data.executor_id,
            user_id=delete_state_data.user_id,
            album_position=delete_state_data.album_position,
            song_position=0,
            is_global_executor=delete_state_data.is_global_executor,
            message=result_message,
        )
    if not result.ok:
        error_message: str = resolve_message(code=result.error.code)
        await callback_update_menu_inline_music_library(
            call=call,
            message=error_message,
            caption=user_messages.USER_PANEL_CAPTION,
        )


@router.message(FSMDeleteSongsAlbumML.state_data)
async def end_delete_songs_album_message(message: Message):
    await message.answer(text=user_messages.CLICK_ONE_OF_THE_BUTTONS_ABOVE)
