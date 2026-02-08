from typing import List, Optional, Set, Dict
from dataclasses import dataclass

from aiogram import Router, Bot, F
from aiogram.types import CallbackQuery, InputMediaPhoto, Message
from aiogram.filters.state import StateFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from app.bot.modules.admin.childes.base_music.filters import (
    BaseDeleteExecutorCallback,
    ConfirmBaseDeleteExecutorCallback,
    BaseDeleteAlbumCallback,
    ConfirmBaseDeleteAlbumCallback,
    BaseDeleteSongMenuCallback,
    BaseButtonDeleteSongCallback,
    ConfirmBaseDeleteSongCallback,
    CancelBaseDeleteSongCallback,
    CompleteBaseDeleteSongCallback,
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
from app.bot.db.uow import UnitOfWork
from app.bot.view_model import SongResponse
from core.error_handlers.helpers import Result
from core.response.response_data import LoggingData


router: Router = Router(name=__name__)

# Удаление исполнителя
@router.callback_query(StateFilter(None), BaseDeleteExecutorCallback.filter())
async def confirm_delete_base_executor(
    call: CallbackQuery,
    callback_data: BaseDeleteExecutorCallback,
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
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result.error.message,
            ),
            reply_markup=get_keyboards_menu_buttons,
        )


@router.callback_query(StateFilter(None), ConfirmBaseDeleteExecutorCallback.filter())
async def delete_executor(
    call: CallbackQuery,
    callback_data: ConfirmBaseDeleteExecutorCallback,
) -> None:
    """Удаление или отмена удаления исполнителя."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    executor_id: Optional[int] = callback_data.executor_id
    if executor_id:

        result: Result = await crud_service.delete_base_executor(
            executor_id=executor_id, logging_data=logging_data
        )
        if result.ok:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption=result.data,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )
        else:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption=result.error.message,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )

    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption="Удаление исполнителя отменено",
            ),
            reply_markup=get_keyboards_menu_buttons,
        )


# Удаление альбома
@router.callback_query(StateFilter(None), BaseDeleteAlbumCallback.filter())
async def confirm_delete_album(
    call: CallbackQuery, callback_data: BaseDeleteAlbumCallback
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
                caption=f"Вы точно хотите удалить альбом исполнителя ?\n\n{result.data}",
            ),
            reply_markup=get_confirmation_delete_album_button(
                executor_id=callback_data.executor_id, album_id=callback_data.album_id
            ),
        )
    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result.error.message,
            ),
            reply_markup=get_keyboards_menu_buttons,
        )


@router.callback_query(StateFilter(None), ConfirmBaseDeleteAlbumCallback.filter())
async def delete_album(
    call: CallbackQuery,
    callback_data: ConfirmBaseDeleteAlbumCallback,
) -> None:
    """Удаление или отмена удаления альбома."""

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    executor_id: Optional[int] = callback_data.executor_id
    album_id: Optional[int] = callback_data.album_id
    if executor_id and album_id:  # если альбом на удаление

        result = await crud_service.delete_base_album(
            executor_id=executor_id,
            logging_data=logging_data,
            album_id=album_id,
        )
        if result.ok:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption="Альбом успешно удален",
                ),
                reply_markup=get_keyboards_menu_buttons,
            )
        else:
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption=result.error.message,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )

    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption="Удаление альбома отменено",
            ),
            reply_markup=get_keyboards_menu_buttons,
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


@router.callback_query(StateFilter(None), BaseDeleteSongMenuCallback.filter())
async def menu_delete_songs(
    call: CallbackQuery,
    callback_data: BaseDeleteSongMenuCallback,
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
                list_songs=array_songs,
                album_id=album_id,
            ),
        ),
    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result.error.message,
            ),
            reply_markup=get_keyboards_menu_buttons,
        ),


@router.callback_query(
    FSMBaseDeleteSongs.state_data, CancelBaseDeleteSongCallback.filter()
)
async def cancel_delete_songs(
    call: CallbackQuery,
    callback_data: CancelBaseDeleteSongCallback,
    state: FSMContext,
):
    """Отменяет удаление песен."""
    await state.clear()

    await call.message.edit_media(
        media=InputMediaPhoto(
            media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
            caption="Удаление песен отменено",
        ),
        reply_markup=get_keyboards_menu_buttons,
    )


@router.message(
    FSMBaseDeleteSongs.state_data,
    F.text,
)
async def get_message_from_delete_songs(
    message: Message,
    bot: Bot,
):
    """Просит нажать на кнопку для отмены удаления песен при вводе текста."""

    await message.answer("Нажмите 'Отменить удаление песен' для выхода в админ панель.")


@router.callback_query(
    FSMBaseDeleteSongs.state_data, BaseButtonDeleteSongCallback.filter()
)
async def delete_songs_buttons(
    call: CallbackQuery,
    callback_data: BaseButtonDeleteSongCallback,
    state: FSMContext,
):
    """Отмечает выбранную песню как готовую к удалению или снимает с удаления."""

    data: Dict = await state.get_data()
    delete_songs: Set = set(data["state_data"].selected_songs_ids)
    songs: List[SongResponse] = data["state_data"].songs

    song_id: int = callback_data.song_id
    album_id: int = callback_data.album_id

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
        ),
    ),


@router.callback_query(
    FSMBaseDeleteSongs.state_data, ConfirmBaseDeleteSongCallback.filter()
)
async def confirm_delete_songs(
    call: CallbackQuery,
    callback_data: ConfirmBaseDeleteSongCallback,
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
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=main_settings.DELETE_IMAGE_FILE_ID,
                    caption=result.error.message,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )

    else:
        await state.clear()

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption="Не было выбрано песен для удаления",
            ),
            reply_markup=get_keyboards_menu_buttons,
        ),


@router.callback_query(
    FSMBaseDeleteSongs.state_data, CompleteBaseDeleteSongCallback.filter()
)
async def delete_songs(
    call: CallbackQuery,
    callback_data: CompleteBaseDeleteSongCallback,
    state: FSMContext,
):
    """Удаляет выбранные песни."""

    data: Dict = await state.get_data()
    await state.clear()

    logging_data: LoggingData = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    delete_songs: List = data["state_data"].selected_songs_ids
    song: SongResponse = data["state_data"].songs[0]

    album_id = song.album_id

    result = await crud_service.delete_songs(
        album_id=album_id,
        songs_ids=delete_songs,
        logging_data=logging_data,
    )

    if result.ok:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption="Удаление песен успешно завершено",
            ),
            reply_markup=get_keyboards_menu_buttons,
        ),
    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result.error.message,
            ),
            reply_markup=get_keyboards_menu_buttons,
        ),
