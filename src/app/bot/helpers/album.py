from typing import Callable, Optional

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from app.bot.services.music_library.show_album_page import (
    ShowAlbumPageService,
    ShowAlbumPageCallbackService,
)
from domain.entities.db.uow import AbstractUnitOfWork
from core.response.response_data import LoggingData


async def return_to_album_page(
    chat_id: int,
    bot: Bot,
    message: str,
    uow: AbstractUnitOfWork,
    logging_data: LoggingData,
    current_page_executor: int,
    album_default_photo_file_id: str,
    limit_songs: int,
    get_information_album: Callable,
    album_id: int,
    executor_id: int,
    user_id: Optional[int],
    album_position: int,
    song_position: int,
    is_global_executor: bool,
    is_admin: bool,
):

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=ReplyKeyboardRemove(),
    )

    await ShowAlbumPageService(uow=uow(), logging_data=logging_data, bot=bot,).execute(
        chat_id=chat_id,
        get_information_album=get_information_album,
        album_default_photo_file_id=album_default_photo_file_id,
        album_id=album_id,
        executor_id=executor_id,
        limit_songs=limit_songs,
        album_position=album_position,
        current_page_executor=current_page_executor,
        song_position=song_position,
        user_id=user_id,
        is_global_executor=is_global_executor,
        is_admin=is_admin,
    )


async def return_to_album_page_callback(
    call: CallbackQuery,
    uow: AbstractUnitOfWork,
    logging_data: LoggingData,
    current_page_executor: int,
    album_default_photo_file_id: str,
    limit_songs: int,
    get_information_album: Callable,
    album_id: int,
    executor_id: int,
    user_id: Optional[int],
    album_position: int,
    song_position: int,
    is_global_executor: bool,
    is_admin: bool = False,
    message: Optional[str] = None,
):
    if message:
        await call.answer(text=message)
    await ShowAlbumPageCallbackService(
        uow=uow(),
        logging_data=logging_data,
        call=call,
    ).execute(
        get_information_album=get_information_album,
        album_default_photo_file_id=album_default_photo_file_id,
        album_id=album_id,
        executor_id=executor_id,
        user_id=user_id,
        limit_songs=limit_songs,
        song_position=song_position,
        album_position=album_position,
        current_page_executor=current_page_executor,
        is_global_executor=is_global_executor,
        is_admin=is_admin,
    )
