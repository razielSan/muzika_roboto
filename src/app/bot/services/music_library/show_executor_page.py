from typing import Union, Callable

from aiogram import Bot
from aiogram.types import InputMediaPhoto, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

from app.bot.modules.music_library.utils.music_library import (
    callback_update_menu_inline_music_library,
    get_inline_menu_music_library,
)
from application.use_cases.db.music_library.get_executor_with_albums import (
    GetExecutorWihtAlbums,
)

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import ExecutorPageResponse
from infrastructure.aiogram.keyboards.inline import (
    show_executor_global_collections,
    show_executor_user_collections,
)
from infrastructure.aiogram.messages import resolve_message, user_messages
from core.response.response_data import Result, LoggingData


class ShowExecutorPageCallbackService:
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
        executor_default_photo_file_id: str,
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
            uow=self.uow, logging_data=self.logging_data
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
                    number_of_albums=len(executor.albums),
                )
                if user_id:  # пользовательская библиотека
                    if executor.is_global:  # глобальный исполнитель
                        try:
                            await self.call.message.edit_media(
                                media=InputMediaPhoto(
                                    caption=info_executor, media=executor.photo_file_id
                                ),
                                reply_markup=show_executor_global_collections(
                                    executor=executor,
                                    limit_albums=limit_albums,
                                    album_position=album_position,
                                    is_sync_executor=False,
                                ),
                            )
                        except TelegramBadRequest:
                            await self.call.answer(
                                text=user_messages.PRESSING_THE_BUTTON_AGAIN_EXECUTOR
                            )
                        return
                    else:  # если пользовательский
                        photo_file_id = (
                            executor.photo_file_id
                            if executor.photo_file_id
                            else executor_default_photo_file_id
                        )
                        try:
                            await self.call.message.edit_media(
                                media=InputMediaPhoto(
                                    caption=info_executor, media=photo_file_id
                                ),
                                reply_markup=show_executor_user_collections(
                                    limit_albums=limit_albums,
                                    executor=executor,
                                    album_position=album_position,
                                ),
                            )
                        except TelegramBadRequest:
                            await self.call.answer(
                                text=user_messages.PRESSING_THE_BUTTON_AGAIN_EXECUTOR
                            )
                        return

                else:  # глобальная библиотека
                    try:
                        await self.call.message.edit_media(
                            media=InputMediaPhoto(
                                caption=info_executor, media=executor.photo_file_id
                            ),
                            reply_markup=show_executor_global_collections(
                                executor=executor,
                                limit_albums=limit_albums,
                                album_position=album_position,
                                is_sync_executor=True,
                            ),
                        )
                    except TelegramBadRequest:
                        await self.call.answer(
                            text=user_messages.PRESSING_THE_BUTTON_AGAIN_EXECUTOR
                        )
                    return

            # если исполнители не были найдены
            not_found_message: str = resolve_message(code=result.code)
            await self.call.answer(text=not_found_message)

            await callback_update_menu_inline_music_library(
                call=self.call, caption=user_messages.USER_PANEL_CAPTION
            )

        if not result.ok:
            error_message: str = resolve_message(code=result.error.code)
            await self.call.answer(text=error_message)


class ShowExecutorPageService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data: LoggingData,
        bot: Bot,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data
        self.bot = bot

    async def execute(
        self,
        chat_id: int,
        get_information_executor: Callable,
        executor_default_photo_file_id: str,
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
            uow=self.uow, logging_data=self.logging_data
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
                    number_of_albums=len(executor.albums),
                )
                if user_id:  # пользовательская библиотека
                    if executor.is_global:  # глобальный исполнитель
                        await self.bot.send_photo(
                            chat_id=chat_id,
                            caption=info_executor,
                            photo=executor.photo_file_id,
                            reply_markup=show_executor_global_collections(
                                executor=executor,
                                limit_albums=limit_albums,
                                album_position=album_position,
                                is_sync_executor=False,
                            ),
                        )

                        return
                    else:  # если пользовательский
                        photo_file_id = (
                            executor.photo_file_id
                            if executor.photo_file_id
                            else executor_default_photo_file_id
                        )
                        await self.bot.send_photo(
                            chat_id=chat_id,
                            caption=info_executor,
                            photo=photo_file_id,
                            reply_markup=show_executor_user_collections(
                                limit_albums=limit_albums,
                                executor=executor,
                                album_position=album_position,
                            ),
                        )
                        return

                else:  # глобальная библиотека
                    await self.bot.send_photo(
                        caption=info_executor,
                        chat_id=chat_id,
                        photo=executor.photo_file_id,
                        reply_markup=show_executor_global_collections(
                            executor=executor,
                            limit_albums=limit_albums,
                            album_position=album_position,
                            is_sync_executor=True,
                        ),
                    )
                    return

            # если исполнители не были найдены
            not_found_message: str = resolve_message(code=result.code)

            await get_inline_menu_music_library(
                chat_id=chat_id,
                bot=self.bot,
                caption=user_messages.USER_PANEL_CAPTION,
                message=not_found_message,
            )

        if not result.ok:
            error_message: str = resolve_message(code=result.error.code)
            await self.bot.send_message(
                text=error_message,
                chat_id=chat_id,
            )
