from typing import Union, Callable

from aiogram import Bot
from aiogram.types import InputMediaPhoto, CallbackQuery

from app.bot.settings import settings as bot_settings
from application.use_cases.db.music_library.get_album_with_songs import (
    GetAlbumWithSongs,
)
from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.aiogram.keyboards.inline import (
    show_album_global,
    show_album_user,
)
from infrastructure.aiogram.messages import resolve_message
from core.response.response_data import Result, LoggingData


class ShowAlbumPageCallbackService:
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
        get_information_album: Callable,
        album_default_photo_file_id: str,
        album_id: int,
        executor_id: int,
        user_id: Union[int, None],
        limit_songs: int,
        song_position=0,
        album_position: int = 0,
        current_page_executor=1,
        is_global_executor=True,
    ) -> Result:
        """
        Application service для callback сценария показа альбома с песнями.

        Отвечает за:
        - отправку сообщений пользователю
        - обработку ошибок
        - взаимодействие с application
        - работу с базой данных

        Содержит логику взаимодействия с Telegram UI.
        """

        response_album = await GetAlbumWithSongs(
            uow=self.uow, logging_data=self.logging_data
        ).execute(
            user_id=user_id,
            executor_id=executor_id,
            album_id=album_id,
            current_page_executor=current_page_executor,
            album_position=album_position,
            is_global_executor=is_global_executor,
        )
        if response_album.ok:
            if response_album.empty:
                not_found_message = resolve_message(code=response_album.code)
                await self.call.message.answer(text=not_found_message)
                return

            album = response_album.data

            info_album: str = get_information_album(
                title=album.title,
                year=album.year,
                number_of_songs=len(album.songs),
            )

            photo_file_id = (
                album.photo_file_id
                if album.photo_file_id
                else album_default_photo_file_id
            )

            if is_global_executor:  # если альбом глобальной библиотеки
                await self.call.message.edit_media(
                    media=InputMediaPhoto(caption=info_album, media=photo_file_id),
                    reply_markup=show_album_global(
                        songs=album.songs,
                        album=album,
                        song_position=song_position,
                        limit_songs=limit_songs,
                        user_id=user_id,
                    ),
                )
            if not is_global_executor:  # если пользовательский альбом
                await self.call.message.edit_media(
                    media=InputMediaPhoto(caption=info_album, media=photo_file_id),
                    reply_markup=show_album_user(
                        songs=album.songs,
                        album=album,
                        song_position=song_position,
                        limit_songs=limit_songs,
                        user_id=user_id,
                    ),
                )

        if not response_album.ok:
            error_message = resolve_message(code=response_album.error.code)
            await self.call.message.answer(text=error_message)


class ShowAlbumPageService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data: LoggingData,
        bot: Bot,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data
        self.bot: Bot = bot

    async def execute(
        self,
        chat_id: int,
        get_information_album: Callable,
        album_default_photo_file_id: str,
        album_id: int,
        executor_id: int,
        user_id: Union[int, None],
        limit_songs: int,
        song_position=0,
        album_position: int = 0,
        current_page_executor=1,
        is_global_executor=True,
    ) -> Result:
        """
        Application service для сценария показа альбома с песнями.

        Отвечает за:
        - отправку сообщений пользователю
        - обработку ошибок
        - взаимодействие с application
        - работу с базой данных

        Содержит логику взаимодействия с Telegram UI.
        """

        response_album = await GetAlbumWithSongs(
            uow=self.uow, logging_data=self.logging_data
        ).execute(
            user_id=user_id,
            executor_id=executor_id,
            album_id=album_id,
            current_page_executor=current_page_executor,
            album_position=album_position,
            is_global_executor=is_global_executor,
        )
        if response_album.ok:
            if response_album.empty:
                not_found_message = resolve_message(code=response_album.code)
                await self.bot.send_message(text=not_found_message)
                return

            album = response_album.data

            info_album = get_information_album(
                title=album.title,
                year=album.year,
                number_of_songs=len(album.songs),
            )

            photo_file_id = (
                album.photo_file_id
                if album.photo_file_id
                else album_default_photo_file_id
            )

            if is_global_executor:  # если альбом глобальной библиотеки
                await self.bot.send_photo(
                    caption=info_album,
                    photo=photo_file_id,
                    chat_id=chat_id,
                    reply_markup=show_album_global(
                        songs=album.songs,
                        album=album,
                        song_position=song_position,
                        limit_songs=limit_songs,
                        user_id=user_id,
                    ),
                )

            if not is_global_executor:  # если пользовательский альбом
                await self.bot.send_photo(
                    caption=info_album,
                    photo=photo_file_id,
                    chat_id=chat_id,
                    reply_markup=show_album_user(
                        songs=album.songs,
                        album=album,
                        song_position=song_position,
                        limit_songs=limit_songs,
                        user_id=user_id,
                    ),
                )

        if not response_album.ok:
            error_message = resolve_message(code=response_album.error.code)
            await self.bot.send_message(text=error_message)
