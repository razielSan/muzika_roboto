from aiogram import Bot
from aiogram.types import CallbackQuery

from application.use_cases.db.music_library.get_song import GetSongAlbum
from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.aiogram.messages import resolve_message
from core.response.response_data import Result, LoggingData


class ShowSongService:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data: LoggingData,
        call: CallbackQuery,
        bot: Bot,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data
        self.call: CallbackQuery = call
        self.bot: Bot = bot

    async def execute(
        self,
        chat_id: int,
        song_id: int,
        album_id: int,
    ) -> Result:
        """
        Application service для сценария сброса песни..

        Отвечает за:
        - отправку сообщений пользователю
        - обработку ошибок
        - взаимодействие с application
        - работу с базой данных

        Содержит логику взаимодействия с Telegram UI.
        """

        response_song = await GetSongAlbum(
            uow=self.uow(), logging_data=self.logging_data
        ).execute(album_id=album_id, song_id=song_id)
        if response_song.ok:
            if response_song.empty:
                not_found_message = resolve_message(code=response_song.code)
                await self.call.message.answer(text=not_found_message)
                return
            song = response_song.data
            await self.bot.send_audio(
                chat_id=chat_id,
                audio=song.file_id,
                caption=f"{song.position}. {song.title}",
            )

        if not response_song.ok:
            error_message = resolve_message(code=response_song.error.code)
            await self.call.message.answer(text=error_message)
