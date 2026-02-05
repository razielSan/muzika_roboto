from typing import Callable

from app.bot.view_model import AlbumResponse
from app.bot.db.uow import UnitOfWork
from core.error_handlers.helpers import ok, fail
from core.response.messages import messages
from core.response.response_data import LoggingData, Result
from core.error_handlers.format import format_errors_message
from app.bot.view_model import SongResponse, AlbumResponse


class BaseMusicService:
    async def show_executor(
        self,
        get_info_executor: Callable[..., str],
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария показа пользователю исполинтеля с альбомами.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            async with UnitOfWork() as uow:
                executors = await uow.executors.get_all_executors()
                if not executors:
                    return fail(
                        code="NOT_FOUND_EXECUTORS",
                        message="Не найденно ни одного исполнителя",
                    )

                executor = executors[0]

                genres = [genre.title for genre in executor.genres]

                data_executor = get_info_executor(
                    name=executor.name,
                    country=executor.country,
                    genres=genres,
                )

                albums_list = [
                    AlbumResponse(
                        title=album.title,
                        year=album.year,
                        executor_id=executor.id,
                        album_id=album.id,
                        executor_photo_file_id=executor.photo_file_id,
                        info_executor=data_executor,
                    )
                    for album in executor.albums
                ]

            albums_list.sort(key=lambda x: x.year)
            return ok(data=albums_list)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.show_executor.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="SHOW_EXECUTOR_ERROR",
                message=messages.SERVER_ERROR,
            )

    async def back_executor(
        self,
        get_info_executor: Callable[..., str],
        logging_data: LoggingData,
        executor_id: int,
    ) -> Result:
        """
        Application service для сценария возврата к исполнителю при нажатии кнопки.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:

            async with UnitOfWork() as uow:
                executor = await uow.executors.get_base_executor(
                    executor_id=executor_id,
                )

                genres = [genre.title for genre in executor.genres]

                data_executor = get_info_executor(
                    name=executor.name,
                    country=executor.country,
                    genres=genres,
                )

                albums_list = [
                    AlbumResponse(
                        title=album.title,
                        year=album.year,
                        executor_id=executor.id,
                        album_id=album.id,
                        executor_photo_file_id=executor.photo_file_id,
                        info_executor=data_executor,
                    )
                    for album in executor.albums
                ]

            albums_list.sort(key=lambda x: x.year)
            return ok(data=albums_list)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.back_executor.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="BACK_EXECUTOR_ERROR",
                message=messages.SERVER_ERROR,
            )

    async def play_song(
        self,
        album_id: int,
        position: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария сброса пользователю песни для прослушивания.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            async with UnitOfWork() as uow:
                song = await uow.songs.get_song_by_position(
                    album_id=album_id, position=position
                )
                song_data = SongResponse(
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                    title=song.title,
                    position=song.position,
                )

            return ok(data=song_data)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.play_song.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="PLAY_SONG_ERROR",
                message=messages.SERVER_ERROR,
            )

    async def show_songs_with_album(
        self,
        executor_id: int,
        album_id: int,
        get_info_album: Callable[..., str],
    ) -> Result:
        """
        Application service для сценария добавления исполнителя в базу данных.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            album = await uow.albums.get_album(
                executor_id=executor_id, album_id=album_id
            )

            info_album = get_info_album(
                title=album.title,
                year=album.year,
            )
            album_photo_file_id = album.photo_file_id
            album_executor_id = album.executor_id
            if album.songs:
                songs = [
                    SongResponse(
                        title=song.title,
                        position=song.position,
                        file_id=song.file_id,
                        file_unique_id=song.file_unique_id,
                        album_title=album.title,
                        album_year=album.year,
                        album_photo_file_id=album.photo_file_id,
                        album_id=album.id,
                        album_executor_id=executor_id,
                        info_album=info_album,
                    )
                    for song in album.songs
                ]
                return ok(data=songs)
            return fail(
                code="ALBUM_NOT_FOUND",
                message="Альбомы для исполнителя не найденны",
                details=SongResponse(
                    album_photo_file_id=album_photo_file_id,
                    album_executor_id=album_executor_id,
                ),
            )


base_music_service: BaseMusicService = BaseMusicService()
