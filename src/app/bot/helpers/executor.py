from typing import Callable, Optional

from aiogram import Bot
from aiogram.types import ReplyKeyboardRemove

from app.bot.services.music_library.show_executor_page import ShowExecutorPageService
from domain.entities.db.uow import AbstractUnitOfWork
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
    user_id: Optional[int],
):

    await bot.send_message(
        chat_id=chat_id,
        text=message,
        reply_markup=ReplyKeyboardRemove(),
    )

    await ShowExecutorPageService(uow=uow(), bot=bot, logging_data=logging_data).execute(
        chat_id=chat_id,
        current_page=current_page_executor,
        limit_albums=limit_albums,
        executor_default_photo_file_id=executor_default_photo_file_id,
        user_id=user_id,
        album_position=album_position,
        get_information_executor=get_information_executor,
    )
