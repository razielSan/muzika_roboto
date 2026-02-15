from typing import List, Optional, Set, Dict
from dataclasses import dataclass

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.childes.base_music.filters import (
    AdminDeleteExecutorCallback,
    AdminConfirmDeleteExecutorCallback,
    AdminDeleteAlbumCallback,
    AdminConfirmDeleteAlbumCallback,
    AdminDeleteSongMenuCallback,
    AdminButtonDeleteSongCallback,
    AdminConfirmDeleteSongCallback,
    AdminCancelDeleteSongCallback,
    AdminCompleteDeleteSongCallback,
    AdminScrollingSongsMenuDeleteCallback,
)
from app.bot.modules.admin.childes.base_music.keyboards.inlinle import (
    get_confirmation_delete_executor_button,
    get_confirmation_delete_album_button,
    get_confirmation_delete_song_button,
    get_menu_song_delete,
)
from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.modules.main.settings import settings as main_settings
from app.bot.modules.admin.childes.base_music.settings import settings
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.modules.admin.childes.base_music.services.crud import crud_service
from core.logging.api import get_loggers
from app.bot.view_model import SongResponse
from app.bot.modules.admin.utils.admin import callback_update_admin_panel_media_photo
from core.error_handlers.helpers import Result
from core.response.response_data import LoggingData
from app.bot.response import LIMIT_SONGS


router: Router = Router(name=__name__)

# Удаление исполнителя
@router.callback_query(StateFilter(None), AdminDeleteExecutorCallback.filter())
async def confirm_delete_base_executor(
    call: CallbackQuery,
    callback_data: AdminDeleteExecutorCallback,
) -> None:
    """Подтверждение на удаление исполнителя."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    executor_id: int = callback_data.executor_id

    result: Result = await crud_service.get_info_executor(
        executor_id=executor_id,
        logging_data=logging_data,
    )

    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=f"Вы точно хотите удалить исполнителя ?\n\n{result.data}",
            ),
            reply_markup=get_confirmation_delete_executor_button(
                executor_id=executor_id,
            ),
        )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(StateFilter(None), AdminConfirmDeleteExecutorCallback.filter())
async def delete_executor(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteExecutorCallback,
) -> None:
    """Удаление или отмена удаления исполнителя."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    executor_id: Optional[int] = callback_data.executor_id
    if executor_id:

        result: Result = await crud_service.delete_base_executor(
            executor_id=executor_id, logging_data=logging_data
        )
        if result.ok:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.data
            )

        else:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.error.message
            )

    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption="Удаление исполнителя отменено"
        )


# Удаление альбома
@router.callback_query(StateFilter(None), AdminDeleteAlbumCallback.filter())
async def confirm_delete_album(
    call: CallbackQuery, callback_data: AdminDeleteAlbumCallback
) -> None:
    """Подтверждение на удаление альбома."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    album_id: int = callback_data.album_id
    executor_id: int = callback_data.executor_id

    result: Result = await crud_service.get_info_album(
        album_id=album_id, executor_id=executor_id, logging_data=logging_data
    )
    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption=f"Вы точно хотите удалить альбом ?\n\n{result.data}",
            ),
            reply_markup=get_confirmation_delete_album_button(
                executor_id=callback_data.executor_id, album_id=callback_data.album_id
            ),
        )
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(StateFilter(None), AdminConfirmDeleteAlbumCallback.filter())
async def delete_album(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteAlbumCallback,
) -> None:
    """Удаление или отмена удаления альбома."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    executor_id: Optional[int] = callback_data.executor_id
    album_id: Optional[int] = callback_data.album_id
    if executor_id and album_id:  # если альбом на удаление

        result: Result = await crud_service.delete_base_album(
            executor_id=executor_id,
            logging_data=logging_data,
            album_id=album_id,
        )
        if result.ok:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.data
            )
        else:
            await callback_update_admin_panel_media_photo(
                call=call, caption=result.error.message
            )

    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption="Удаление альбома отменено"
        )


# Удаление песен альбома
class FSMBaseDeleteSongs(StatesGroup):
    """FSM для сценария удаления песен."""

    state_data: State = State()


@dataclass
class SongsDeleteResponse:
    """Хранит данные для удаления песен."""

    songs: List[SongResponse]
    selected_songs_ids: List[int]


@router.callback_query(StateFilter(None), AdminDeleteSongMenuCallback.filter())
async def menu_delete_songs(
    call: CallbackQuery,
    callback_data: AdminDeleteSongMenuCallback,
    state: FSMContext,
) -> None:
    """
    Возращает inline menu с возможность выбрать песни для удаления.
    """

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    album_id: int = callback_data.album_id

    result: Result = await crud_service.show_menu_songs_delete(
        album_id=album_id,
        logging_data=logging_data,
    )
    if result.ok:
        array_songs: List[SongResponse] = result.data
        len_list_songs = len(array_songs)

        songs = array_songs[0:5]

        await state.update_data(
            state_data=SongsDeleteResponse(
                songs=array_songs,
                selected_songs_ids=set(),
            )
        )
        await state.set_state(FSMBaseDeleteSongs.state_data)
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption="Выберите песни для удаления",
            ),
            reply_markup=get_menu_song_delete(
                list_songs=songs,
                album_id=album_id,
                len_list_songs=len_list_songs,
                song_position=0,
            ),
        ),
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminCancelDeleteSongCallback.filter()
)
async def cancel_delete_songs(
    call: CallbackQuery,
    callback_data: AdminCancelDeleteSongCallback,
    state: FSMContext,
):
    """Отменяет удаление песен."""
    await state.clear()

    await callback_update_admin_panel_media_photo(
        call=call,
        caption="Удаление песен отменено",
    )


@router.message(
    FSMBaseDeleteSongs.state_data,
    F.text,
)
async def get_message_from_delete_songs(
    message: Message,
):
    """Просит нажать на кнопку для отмены удаления песен при вводе текста."""

    await message.answer("Нажмите 'Отменить удаление песен' для выхода в админ панель.")


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminButtonDeleteSongCallback.filter()
)
async def delete_songs_buttons(
    call: CallbackQuery,
    callback_data: AdminButtonDeleteSongCallback,
    state: FSMContext,
):
    """Отмечает выбранную песню как готовую к удалению или снимает с удаления."""

    data: Dict = await state.get_data()
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    songs: List[SongResponse] = data["state_data"].songs
    len_list_songs: int = len(songs)  # получаем общее количество песен до изменения

    song_id: int = callback_data.song_id
    album_id: int = callback_data.album_id
    position: int = callback_data.position

    songs = songs[position : position + 5]  # измененяем песни с учетом позиции

    if song_id in delete_songs:  # если песня уже есть на удаление- убирает ее
        delete_songs.remove(song_id)
    else:  # если песни нету на удаление - добавляем ее
        delete_songs.add(song_id)

    data["state_data"].selected_songs_ids = list(delete_songs)  # сохраняем списком

    await state.update_data(state_data=data["state_data"])  # обновляем состояние

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=main_settings.DELETE_IMAGE_FILE_ID,
            caption="Выберите песни для удаления",
        ),
        reply_markup=get_menu_song_delete(
            list_songs=songs,
            delete_songs=delete_songs,
            album_id=album_id,
            song_position=position,
            limit_songs=LIMIT_SONGS,
            len_list_songs=len_list_songs,
        ),
    ),


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminScrollingSongsMenuDeleteCallback.filter()
)
async def scrolling_songe_menu_delete(
    call: CallbackQuery,
    callback_data: AdminScrollingSongsMenuDeleteCallback,
    state: FSMContext,
):
    """Пролистывает песни из меню удаления песен."""

    data: Dict = await state.get_data()

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    album_id: int = callback_data.album_id
    position: int = callback_data.position + callback_data.offset
    delete_songs: Set = set(data["state_data"].selected_songs_ids)

    result: Result = await crud_service.show_menu_songs_delete(
        album_id=album_id,
        logging_data=logging_data,
    )
    if result.ok:
        songs: List[SongResponse] = result.data
        len_list_songs: int = len(songs)

        songs = songs[position : position + 5]

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=main_settings.DELETE_IMAGE_FILE_ID,
                caption="Выберите песни для удаления",
            ),
            reply_markup=get_menu_song_delete(
                len_list_songs=len_list_songs,
                album_id=album_id,
                song_position=position,
                limit_songs=LIMIT_SONGS,
                list_songs=songs,
                delete_songs=delete_songs,
            ),
        ),
    else:
        await callback_update_admin_panel_media_photo(
            call=call, caption=result.error.message
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminConfirmDeleteSongCallback.filter()
)
async def confirm_delete_songs(
    call: CallbackQuery,
    callback_data: AdminConfirmDeleteSongCallback,
    state: FSMContext,
) -> None:
    """Подтверждение на удаление песни."""

    data: Dict = await state.get_data()

    delete_songs: Set = data["state_data"].selected_songs_ids

    if delete_songs:

        album_id: int = callback_data.album_id
        logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

        result: Result = await crud_service.get_positions_songs(
            album_id=album_id,
            songs_ids=delete_songs,
            logging_data=logging_data,
        )
        if result.ok:
            songs: List = result.data
            count: int = len(songs)
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=main_settings.DELETE_IMAGE_FILE_ID,
                    caption=f"Вы действительно хотите удалить песни ?"
                    f"\n\nКоличество песен: {count}\nНомера позиций песен: {str(songs)}",
                ),
                reply_markup=get_confirmation_delete_song_button(),
            )
        else:
            await state.clear()

            await callback_update_admin_panel_media_photo(
                call=call,
                caption=result.error.message,
            )

    else:
        await state.clear()

        await callback_update_admin_panel_media_photo(
            call=call,
            caption="Не было выбрано песен для удаления",
        )


@router.callback_query(
    FSMBaseDeleteSongs.state_data, AdminCompleteDeleteSongCallback.filter()
)
async def delete_songs(
    call: CallbackQuery,
    callback_data: AdminCompleteDeleteSongCallback,
    state: FSMContext,
):
    """Удаляет выбранные песни."""

    data: Dict = await state.get_data()
    await state.clear()

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    delete_songs: List = data["state_data"].selected_songs_ids
    song: SongResponse = data["state_data"].songs[0]

    album_id: int = song.album_id

    result: Result = await crud_service.delete_songs(
        album_id=album_id,
        songs_ids=delete_songs,
        logging_data=logging_data,
    )

    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result.data,
            ),
            reply_markup=get_keyboards_menu_buttons,
        ),
    else:
        await callback_update_admin_panel_media_photo(
            call=call,
            caption=result.error.message,
        )
