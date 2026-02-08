from typing import Set, List

from app.bot.db.uow import UnitOfWork
from core.error_handlers.helpers import ok, fail
from core.response.response_data import LoggingData
from core.error_handlers.format import format_errors_message
from app.bot.utils.editing import get_info_executor, get_info_album
from core.error_handlers.helpers import Result
from app.bot.view_model import SongResponse


class CRUDService:
    async def delete_base_executor(
        self,
        executor_id: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария удаление исполнителя.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            executor = None
            async with UnitOfWork() as uow:
                executor = await uow.executors.get_base_executor(
                    executor_id=executor_id,
                )
                if executor:
                    await uow.executors.delete_base_executor(executor_id=executor_id)
                else:
                    return fail(
                        code="EXECUTOR_NOT_FOUND", message="Исполнитель не найден"
                    )

            return ok(data="Исполнитель успешно удален")
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.delete_base_executor.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при удалении исполнителя",
            )

    async def get_info_executor(
        self,
        executor_id: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария получения информации о исполнителе.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            executor = None
            info_executor = None
            async with UnitOfWork() as uow:
                executor = await uow.executors.get_base_executor(
                    executor_id=executor_id,
                )

                if not executor:
                    return fail(
                        code="EXECUTOR_NOT_FOUND", message="Исполнитель не найден"
                    )

                genres = [genre.title for genre in executor.genres]
                info_executor = get_info_executor(
                    name=executor.name, country=executor.country, genres=genres
                )

            return ok(data=info_executor)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.get_info_executor.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при получении информации об исполнителе",
            )

    async def get_info_album(
        self,
        album_id: int,
        executor_id: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария получения информации о альбоме.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            album = None
            info_album = None
            async with UnitOfWork() as uow:
                album = await uow.albums.get_album(
                    executor_id=executor_id, album_id=album_id
                )
                if not album:
                    return fail(code="ALBUM_NOT_FOUND", message="Альбом не найден")
                info_album = get_info_album(title=album.title, year=album.year)

            return ok(data=info_album)

        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.get_info_album.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при получении информации о альбоме",
            )

    async def delete_base_album(
        self,
        executor_id: int,
        album_id: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария удаления альбома..

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            async with UnitOfWork() as uow:
                await uow.albums.delete_album(
                    executor_id=executor_id, album_id=album_id
                )

            return ok(data="Альбома успешно удален")
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.delete_base_album.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при удалении альбома исполнителя",
            )

    async def show_menu_songs_delete(
        self,
        album_id: int,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария показа меню удаления песен..

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            async with UnitOfWork() as uow:
                result = await uow.songs.get_all_songs(album_id=album_id)
                array_songs = [
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
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.show_menu_songs_delete.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при получении песен для меню удаления песен.",
            )

    async def get_positions_songs(
        self,
        album_id: int,
        songs_ids: List,
        logging_data: LoggingData,
    ) -> Result:
        """
        Application service для сценария поиска позиций песен.

        Отвечает за:
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        try:
            async with UnitOfWork() as uow:
                result: List[int] = await uow.songs.get_positions_songs_by_id(
                    album_id=album_id,
                    songs_ids=songs_ids,
                )

            return ok(data=result)
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.get_positions_songs.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при получениt позиций песен.",
            )

    async def delete_songs(
        self,
        album_id: int,
        songs_ids: List,
        logging_data: LoggingData,
    ):
        try:
            async with UnitOfWork() as uow:
                await uow.songs.delete_songs(
                    album_id=album_id,
                    list_ids=songs_ids,
                )
            return ok(data="success")
        except Exception as err:
            logging_data.error_logger.exception(
                format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.delete_songs.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="UNKNOWN_ERROR",
                message="Неизвестная ошибка при удалении песен.",
            )


crud_service: CRUDService = CRUDService()
