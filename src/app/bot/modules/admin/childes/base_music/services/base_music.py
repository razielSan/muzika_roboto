from typing import Callable, List

from app.bot.view_model import AlbumResponse
from app.bot.db.uow import UnitOfWork
from core.error_handlers.helpers import ok, fail
from core.response.response_data import LoggingData, Result
from app.bot.view_model import (
    SongResponse,
    AlbumResponse,
    ExecutorResponse,
    ExecutorPageRepsonse,
)
from core.error_handlers.decorator import safe_async_execution
from app.bot.response import ServerDatabaseResponse


class BaseMusicService:
    @safe_async_execution(
        message=ServerDatabaseResponse.ERROR_SHOW_EXECUTOR.value,
        code=ServerDatabaseResponse.ERROR_SHOW_EXECUTOR.name,
    )
    async def show_executor(
        self,
        get_info_executor: Callable[..., str],
        logging_data: LoggingData,
        page_executor: int = 1,
    ) -> Result:
        """
        Application service для сценария показа исполнителя с альбомами.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        photo_file_id = None
        executor_id = None
        count_executors = None
        async with UnitOfWork() as uow:
            executors = await uow.executors.get_all_executors()
            if not executors:
                return fail(
                    code=ServerDatabaseResponse.NOT_FOUND_EXECUTORS.name,
                    message=ServerDatabaseResponse.NOT_FOUND_EXECUTORS.value,
                )
            count_executors: int = len(executors)

            executor = executors[page_executor - 1]
            photo_file_id: str = executor.photo_file_id
            executor_id: int = executor.id

            genres: List[str] = [genre.title for genre in executor.genres]

            data_executor: str = get_info_executor(
                name=executor.name,
                country=executor.country,
                genres=genres,
            )

            albums_list: List[str] = [
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
        return ok(
            data=ExecutorPageRepsonse(
                executor=ExecutorResponse(
                    info_executor=data_executor,
                    executor_id=executor_id,
                    photo_file_id=photo_file_id,
                ),
                albums=albums_list,
                total_pages=count_executors,
                current_page=page_executor,
            )
        )

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_BACK_EXECUTOR.name,
        message=ServerDatabaseResponse.ERROR_BACK_EXECUTOR.value,
    )
    async def back_executor(
        self,
        get_info_executor: Callable[..., str],
        logging_data: LoggingData,
        current_page_executor: int,
    ) -> Result:
        """
        Application service для сценария возврата к исполнителю при нажатии кнопки.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            executors = await uow.executors.get_all_executors()

            executor = executors[current_page_executor - 1]

            genres: List[str] = [genre.title for genre in executor.genres]

            data_executor: str = get_info_executor(
                name=executor.name,
                country=executor.country,
                genres=genres,
            )

            albums_list: List[AlbumResponse] = [
                AlbumResponse(
                    title=album.title,
                    year=album.year,
                    executor_id=executor.id,
                    album_id=album.id,
                    executor_photo_file_id=executor.photo_file_id,
                    info_executor=data_executor,
                    count_executors=len(executors),
                )
                for album in executor.albums
            ]

        albums_list.sort(key=lambda x: x.year)
        return ok(data=albums_list)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_PLAY_SONG.name,
        message=ServerDatabaseResponse.ERROR_PLAY_SONG.value,
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
        async with UnitOfWork() as uow:
            song = await uow.songs.get_song_by_position(
                album_id=album_id, position=position
            )
            song_data: SongResponse = SongResponse(
                file_id=song.file_id,
                file_unique_id=song.file_unique_id,
                title=song.title,
                position=song.position,
            )

        return ok(data=song_data)

    async def show_songs_with_album(
        self,
        executor_id: int,
        album_id: int,
        get_info_album: Callable[..., str],
    ) -> Result:
        """
        Application service для сценария добавления показа альбома с песнями..

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

            info_album: str = get_info_album(
                title=album.title,
                year=album.year,
            )
            album_photo_file_id: str = album.photo_file_id
            album_executor_id: int = album.executor_id
            if album.songs:
                songs: List[SongResponse] = [
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
                code=ServerDatabaseResponse.NOT_FOUND_SONGS.name,
                message=ServerDatabaseResponse.NOT_FOUND_SONGS.value,
                details=SongResponse(
                    album_photo_file_id=album_photo_file_id,
                    album_executor_id=album_executor_id,
                ),
            )


base_music_service: BaseMusicService = BaseMusicService()
