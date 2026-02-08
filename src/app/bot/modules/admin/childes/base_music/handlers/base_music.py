from typing import List

from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaPhoto
from aiogram.filters.state import StateFilter

from app.bot.modules.admin.childes.base_music.settings import settings
from app.bot.modules.admin.settings import settings as admin_settings
from app.bot.modules.admin.childes.base_music.keyboards.inlinle import (
    show_one_album_songs_with_base_executor,
)
from app.bot.modules.admin.childes.base_music.services.base_music import (
    base_music_service,
)
from core.logging.api import get_loggers
from app.bot.view_model import SongResponse
from app.bot.modules.admin.response import get_keyboards_menu_buttons
from app.bot.utils.editing import get_info_album, get_info_executor
from app.bot.modules.admin.childes.base_music.filters import (
    BackExecutorCallback,
    BaseMusicCallback,
    BasePlaySongCallback,
)
from app.bot.modules.admin.childes.base_music.keyboards.inlinle import (
    show_base_executor_collections,
)
from app.bot.view_model import ExecutorResponse, AlbumResponse


router: Router = Router(name=__name__)


@router.callback_query(StateFilter(None), F.data == settings.MENU_CALLBACK_DATA)
async def base_music(call: CallbackQuery) -> None:
    """Возвращает первого исполнителя из базового музыкального хранилища."""

    print("base_music")
    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_executor = await base_music_service.show_executor(
        get_info_executor=get_info_executor, logging_data=logging_data
    )
    if result_executor.ok:
        executor: ExecutorResponse = result_executor.data
        albums_list: List[AlbumResponse] = executor.albums_list
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=executor.photo_file_id,
                caption=executor.info_executor,
            ),
            reply_markup=show_base_executor_collections(
                list_albums=albums_list,
                executor_id=executor.executor_id,
            ),
        )
    else:
        try:  # При повторном нажатии кнопки когда нет исполнителей
            await call.message.edit_media(
                media=InputMediaPhoto(
                    media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                    caption=result_executor.error.message,
                ),
                reply_markup=get_keyboards_menu_buttons,
            )
        except Exception:
            pass


@router.callback_query(StateFilter(None), BaseMusicCallback.filter())
async def show_songs_with_album(
    call: CallbackQuery,
    bot: Bot,
    callback_data: BaseMusicCallback,
) -> None:
    """Возвращает альбом со списком песен для исполнителя."""

    executor_id: int = callback_data.executor_id
    album_id: int = callback_data.album_id

    result = await base_music_service.show_songs_with_album(
        executor_id=executor_id,
        album_id=album_id,
        get_info_album=get_info_album,
    )
    if result.ok:
        songs = result.data
        song: SongResponse = result.data[0]
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=song.album_photo_file_id,
                caption=song.info_album,
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=songs,
                executor_id=song.album_executor_id,
                album_id=album_id,
            ),
        )
    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=song.album_photo_file_id,
                caption=result.error.message,
            ),
            reply_markup=show_one_album_songs_with_base_executor(
                list_songs=[],
                executor_id=song.album_executor_id,
            ),
        )


@router.callback_query(StateFilter(None), BackExecutorCallback.filter())
async def back_to_executor(
    call: CallbackQuery,
    callback_data: BackExecutorCallback,
) -> None:
    """Возвращает назад к исполнителю, при нажатии кнопки."""

    executor_id: int = callback_data.executor_id

    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)

    result_executor = await base_music_service.back_executor(
        get_info_executor=get_info_executor,
        logging_data=logging_data,
        executor_id=executor_id,
    )

    if result_executor.ok:
        albums_list = result_executor.data
        album = albums_list[0]

        await call.message.edit_media(
            media=InputMediaPhoto(
                media=album.executor_photo_file_id,
                caption=album.info_executor,
            ),
            reply_markup=show_base_executor_collections(
                list_albums=albums_list, executor_id=executor_id
            ),
        )
    else:
        await call.message.edit_media(
            media=InputMediaPhoto(
                media=admin_settings.ADMIN_PANEL_PHOTO_FILE_ID,
                caption=result_executor.error.message,
            ),
            reply_markup=get_keyboards_menu_buttons,
        )


@router.callback_query(StateFilter(None), BasePlaySongCallback.filter())
async def play_song(
    call: CallbackQuery,
    callback_data: BasePlaySongCallback,
    bot: Bot,
) -> None:
    """Скидывает песню для прослушивания."""

    logging_data = get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
    position: int = callback_data.position
    album_id: int = callback_data.album_id

    result = await base_music_service.play_song(
        album_id=album_id,
        position=position,
        logging_data=logging_data,
    )

    if result.ok:
        song = result.data
        await bot.send_audio(
            chat_id=call.message.chat.id,
            audio=song.file_id,
        )
    else:
        await call.message.answer(text=result.error.message)
