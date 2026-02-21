from typing import List, Optional

from app.bot.db.uow import UnitOfWork
from core.error_handlers.helpers import ok, fail
from core.response.response_data import LoggingData
from app.bot.utils.editing import get_info_executor, get_info_album
from core.error_handlers.helpers import Result
from app.bot.view_model import SongResponse
from app.bot.response import ServerDatabaseResponse
from core.error_handlers.decorator import safe_async_execution
from core.logging.api import get_loggers
from app.bot.modules.admin.childes.base_music.settings import settings


class CRUDService:
    def __init__(self, logging_data: LoggingData):
        self.logging_data = logging_data

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_INFO_EXECUTOR.name,
        message=ServerDatabaseResponse.ERROR_INFO_EXECUTOR.value,
    )
    async def get_info_executor(
        self,
        executor_id: int,
    ) -> Result:
        """
        Application service для сценария получения информации о исполнителе.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        executor = None
        info_executor = None
        async with UnitOfWork() as uow:
            executor = await uow.executors.get_base_executor(
                executor_id=executor_id,
            )

            if not executor:
                return fail(
                    code=ServerDatabaseResponse.NOT_FOUND_EXECUTOR.name,
                    message=ServerDatabaseResponse.NOT_FOUND_EXECUTOR.value,
                )

            genres = [genre.title for genre in executor.genres]
            info_executor = get_info_executor(
                name=executor.name, country=executor.country, genres=genres
            )

        return ok(data=info_executor)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_INFO_ALBUM.name,
        message=ServerDatabaseResponse.ERROR_INFO_ALBUM.value,
    )
    async def get_info_album(
        self,
        album_id: int,
        executor_id: int,
    ) -> Result:
        """
        Application service для сценария получения информации о альбоме.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        album = None
        info_album = None
        async with UnitOfWork() as uow:
            album = await uow.albums.get_album(
                executor_id=executor_id, album_id=album_id
            )
            if not album:
                return fail(
                    code=ServerDatabaseResponse.NOT_FOUND_ALBUM.name,
                    message=ServerDatabaseResponse.NOT_FOUND_ALBUM.value,
                )
            info_album = get_info_album(title=album.title, year=album.year)

        return ok(data=info_album)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_POSITIONS_SONGS.name,
        message=ServerDatabaseResponse.ERROR_POSITIONS_SONGS.value,
    )
    async def get_positions_songs(
        self,
        album_id: int,
        songs_ids: List,
    ) -> Result:
        """
        Application service для сценария поиска позиций песен.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            result: List[int] = await uow.songs.get_positions_songs_by_id(
                album_id=album_id,
                songs_ids=songs_ids,
            )

        return ok(data=result)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_MENU_SONGS_DELETE.name,
        message=ServerDatabaseResponse.ERROR_MENU_SONGS_DELETE.value,
    )
    async def show_menu_songs_delete(
        self,
        album_id: int,
    ) -> Result:
        """
        Application service для сценария показа меню удаления песен..

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            result = await uow.songs.get_all_songs(album_id=album_id)
            array_songs: List[SongResponse] = [
                SongResponse(
                    position=song.position,
                    album_id=song.album_id,
                    title=song.title,
                    song_id=song.id,
                )
                for song in result
            ]
        return ok(
            data=array_songs,
        )

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_PHOTO_EXECUTOR.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_PHOTO_EXECUTOR.value,
    )
    async def update_photo_executor(
        self,
        executor_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Result:
        """
        Application service для сценария обновления фото исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.executors.update_photo_file_id_and_photo_file_unique_id(
                executor_id=executor_id,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_PHOTO_EXECUTOR.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_PHOTO_ALBUM.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_PHOTO_ALBUM.value,
    )
    async def update_album_photo(
        self,
        executor_id: int,
        album_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Result:
        """
        Application service для сценария обновления фото альбома.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.albums.update_photo_file_id_and_photo_file_unique_id(
                executor_id=executor_id,
                album_id=album_id,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_PHOTO_ALBUM.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_NAME.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_NAME.value,
    )
    async def update_executor_name(
        self,
        executor_id: int,
        name: str,
    ) -> Result:
        """
        Application service для сценария обновления имени исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.executors.update_name(
                executor_id=executor_id,
                name=name,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_EXECUTOR_NAME.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_COUNTRY.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_COUNTRY.value,
    )
    async def update_executor_country(
        self,
        executor_id: int,
        country: str,
    ) -> Result:
        """
        Application service для сценария обновления страны исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.executors.update_country(
                executor_id=executor_id,
                country=country,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_EXECUTOR_COUNTRY.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_ALBUM_TITLE.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_ALBUM_TITLE.value,
    )
    async def update_album_tilte(
        self,
        executor_id: int,
        album_id: int,
        title: str,
    ) -> Result:
        """
        Application service для сценария обновления заголовка альбома.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.albums.update_title(
                executor_id=executor_id,
                album_id=album_id,
                title=title,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_ALBUM_TITLE.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_ALBUM_YEAR.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_ALBUM_YEAR.value,
    )
    async def update_album_year(
        self,
        executor_id: int,
        album_id: int,
        year: str,
    ) -> Result:
        """
        Application service для сценария обновления года выпуса альбома.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.albums.update_year(
                executor_id=executor_id,
                album_id=album_id,
                year=year,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_ALBUM_YEAR.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_GENRES.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_EXECUTOR_GENRES.value,
    )
    async def update_executor_genres(
        self,
        executor_id: int,
        genres: List[str],
    ) -> Result:
        """
        Application service для сценария обновления жанров исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            update_genres = await uow.genres.get_or_create_genres(titles=genres)

            await uow.executors.update_genres_base_executor(
                genres=update_genres, excutor_id=executor_id
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_EXECUTOR_GENRES.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_UPDATE_TITLE_SONG.name,
        message=ServerDatabaseResponse.ERROR_UPDATE_TITLE_SONG.value,
    )
    async def update_title_song(
        self, album_id: int, position: int, title: int
    ) -> Result:
        """
        Application service для сценария обновления имени песни.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            song = await uow.songs.update_title_song(
                album_id=album_id,
                position=position,
                title=title,
            )
        if song:
            return ok(data=ServerDatabaseResponse.SUCCESS_UPDATE_TITLE_SONG.value)
        return ok(
            empty=True, data=ServerDatabaseResponse.NOT_FOUND_TITLE_SONG_POSITION.value
        )  # Если в альбоме нет песен с указанной позицией

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_ADD_ALBUM.name,
        message=ServerDatabaseResponse.ERROR_ADD_ALBUM.value,
    )
    async def create_album(
        self,
        executor_id: int,
        title: str,
        year: str,
        photo_file_unique_id: str,
        photo_file_id: str,
        songs: List[SongResponse],
    ) -> Result:
        """
        Application service для сценария создания альбома с песнями.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        album_id = None
        async with UnitOfWork() as uow:
            executor = await uow.executors.get_base_executor(executor_id=executor_id)
            album = await uow.albums.create_album(
                executor=executor,
                title=title,
                year=year,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )

            album_id: int = album.id
            await uow.songs.create_songs(
                song_repsonse=songs,
                album_id=album_id,
                start_position=1,
            )
        return ok(data=album_id)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_ADD_SONGS.name,
        message=ServerDatabaseResponse.ERROR_ADD_SONGS.value,
    )
    async def add_songs(
        self,
        album_id: int,
        songs: List[SongResponse],
    ) -> Result:
        """
        Application service для сценария добавления песен в альбом.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            position: Optional[int] = await uow.songs.get_last_poistion_song(
                album_id=album_id
            )
            position: int = 0 if not position else position
            start_position: int = position + 1
            await uow.songs.create_songs(
                song_repsonse=songs, album_id=album_id, start_position=start_position
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_ADD_SONGS.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_DELETE_EXECUTOR.name,
        message=ServerDatabaseResponse.ERROR_DELETE_EXECUTOR.value,
    )
    async def delete_base_executor(
        self,
        executor_id: int,
    ) -> Result:
        """
        Application service для сценария удаление исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        executor = None
        async with UnitOfWork() as uow:
            executor = await uow.executors.get_base_executor(
                executor_id=executor_id,
            )
            if executor:
                await uow.executors.delete_base_executor(executor_id=executor_id)
            else:
                return fail(
                    code=ServerDatabaseResponse.NOT_FOUND_EXECUTOR.name,
                    message=ServerDatabaseResponse.NOT_FOUND_EXECUTOR.value,
                )

        return ok(data=ServerDatabaseResponse.SUCCESS_DELETE_EXECUTOR.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_DELETE_ALBUM.name,
        message=ServerDatabaseResponse.ERROR_DELETE_ALBUM.value,
    )
    async def delete_base_album(
        self,
        executor_id: int,
        album_id: int,
    ) -> Result:
        """
        Application service для сценария удаления альбома..

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.albums.delete_album(executor_id=executor_id, album_id=album_id)

        return ok(data=ServerDatabaseResponse.SUCCESS_DELETE_ALBUM.value)

    @safe_async_execution(
        code=ServerDatabaseResponse.ERROR_DELETE_SONGS.name,
        message=ServerDatabaseResponse.ERROR_DELETE_SONGS.value,
    )
    async def delete_songs(
        self,
        album_id: int,
        songs_ids: List,
    ) -> Result:
        """
        Application service для сценария удаления песен из альбома.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        async with UnitOfWork() as uow:
            await uow.songs.delete_songs(
                album_id=album_id,
                list_ids=songs_ids,
            )
        return ok(data=ServerDatabaseResponse.SUCCESS_DELETE_SONGS.value)


crud_service: CRUDService = CRUDService(
    logging_data=get_loggers(name=settings.NAME_FOR_LOG_FOLDER),
)
