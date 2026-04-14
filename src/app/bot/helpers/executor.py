from typing import Callable, Optional

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from app.bot.services.music_library.show_executor_page import (
    ShowExecutorPageService,
    ShowExecutorPageCallbackService,
)
from infrastructure.db.db_helper import db_helper
from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import LibraryMode
from core.response.response_data import LoggingData


async def return_to_executor_page(
    chat_id: int,
    bot: Bot,
    message: str,
    uow: AbstractUnitOfWork,
    logging_data: LoggingData,
    current_page_executor: int,
    executor_default_photo_file_id: str,
    limit_albums: int,
    album_position: int,
    get_information_executor: Callable,
    mode=LibraryMode,
):

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=ReplyKeyboardRemove(),
    )

    await ShowExecutorPageService(
        uow=uow(session_factory=db_helper.session), bot=bot, logging_data=logging_data
    ).execute(
        chat_id=chat_id,
        current_page=current_page_executor,
        limit_albums=limit_albums,
        executor_default_photo_file_id=executor_default_photo_file_id,
        mode=mode,
        album_position=album_position,
        get_information_executor=get_information_executor,
    )


async def return_to_executor_page_callback(
    call: CallbackQuery,
    uow: AbstractUnitOfWork,
    logging_data: LoggingData,
    current_page_executor: int,
    executor_default_photo_file_id: str,
    limit_albums: int,
    album_position: int,
    get_information_executor: Callable,
    mode: LibraryMode,
    message: Optional[str] = None,
):
    if message:
        await call.answer(text=message)
    await ShowExecutorPageCallbackService(
        uow=uow(session_factory=db_helper.session), logging_data=logging_data, call=call
    ).execute(
        get_information_executor=get_information_executor,
        executor_default_photo_file_id=executor_default_photo_file_id,
        mode=mode,
        limit_albums=limit_albums,
        album_position=album_position,
        current_page=current_page_executor,
    )
