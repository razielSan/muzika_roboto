from typing import Union, Callable

from aiogram.types import InputMediaPhoto, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from application.use_cases.db.music_library.get_executor_with_albums import (
    GetExecutorWihtAlbums,
)
from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import ExecutorPageResponse
from infrastructure.aiogram.keyboards.inline import show_executor_global_collections
from infrastructure.aiogram.messages import resolve_message, user_messages
from core.response.response_data import Result, LoggingData


class ShowExecutorPageService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data: LoggingData,
        call: CallbackQuery,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data
        self.call: CallbackQuery = call

    async def execute(
        self,
        get_information_executor: Callable,
        EXECUTOR_DEFAULT_PHOTO_FILE_ID: str,
        user_id: Union[int, None],
        limit_albums: int,
        album_position=0,
        current_page=1,
    ) -> Result:
        """
        Application service для сценария пока исполнителя с альбомами.

        Отвечает за:
        - отправку сообщений пользователю
        - обработку ошибок
        - взаимодействие с application
        - работу с базой данных

        Содержит логику взаимодействия с Telegram UI.
        """
        result: Result = await GetExecutorWihtAlbums(
            uow=self.uow(), logging_data=self.logging_data
        ).execute(
            user_id=user_id,
            current_page=current_page,
        )
        if result.ok:
            if not result.empty:
                executor: ExecutorPageResponse = result.data
                info_executor = get_information_executor(
                    name=executor.name,
                    country=executor.country,
                    genres=executor.genres,
                    len_albums=len(executor.albums),
                )
                try:
                    await self.call.message.edit_media(
                        media=InputMediaPhoto(
                            caption=info_executor, media=executor.photo_file_id
                        ),
                        reply_markup=show_executor_global_collections(
                            executor=executor,
                            limit_albums=limit_albums,
                            album_position=album_position,
                        ),
                    )
                except TelegramBadRequest:
                    await self.call.answer(
                        text=user_messages.PRESSING_THE_BUTTON_AGAIN_EXECUTOR
                    )
                return

            # если исполнители не были найдены
            not_found_message: str = resolve_message(code=result.code)
            await self.call.message.edit_media(
                media=InputMediaPhoto(
                    caption=not_found_message,
                    media=EXECUTOR_DEFAULT_PHOTO_FILE_ID,
                ),
                reply_markup=show_executor_global_collections(
                    executor=None,
                    limit_albums=limit_albums,
                    album_position=album_position,
                ),
            )
            return
        if not result.ok:
            error_message: str = resolve_message(code=result.error.code)
            await self.call.message.answer(text=error_message)
