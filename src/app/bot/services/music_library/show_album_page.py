from typing import Union, Callable

from aiogram.types import InputMediaPhoto, CallbackQuery

from application.use_cases.db.music_library.get_album_with_songs import (
    GetAlbumWithSongs,
)
from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.aiogram.keyboards.inline import show_album_collections
from infrastructure.aiogram.messages import resolve_message
from core.response.response_data import Result, LoggingData


class ShowAlbumPageService:
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
        album_id: int,
        executor_id: int,
        user_id: Union[int, None],
        limit_songs: int,
        song_position=0,
        album_position: int = 0,
        current_page_executor=1,
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
            uow=self.uow(), logging_data=self.logging_data
        ).execute(
            user_id=user_id,
            executor_id=executor_id,
            album_id=album_id,
            current_page_executor=current_page_executor,
            album_position=album_position,
        )
        if response_album.ok:
            if response_album.empty:
                not_found_message = resolve_message(code=response_album.code)
                await self.call.message.answer(text=not_found_message)
                return

            album = response_album.data

            info_album = get_information_album(
                title=album.title,
                year=album.year,
                number_of_songs=len(album.songs),
            )
            await self.call.message.edit_media(
                media=InputMediaPhoto(caption=info_album, media=album.photo_file_id),
                reply_markup=show_album_collections(
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
