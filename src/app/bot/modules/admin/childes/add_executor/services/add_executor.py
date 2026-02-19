from typing import List, Callable, Set, Awaitable
from pathlib import Path

from aiogram.types import Message

from app.bot.modules.admin.childes.add_executor.api.add_executor import add_executor_api
from app.bot.modules.admin.childes.add_executor.settings import settings
from app.bot.settings import settings
from app.bot.db.uow import UnitOfWork
from app.bot.view_model import SongResponse
from core.error_handlers.helpers import ok, fail
from core.response.response_data import LoggingData, Result
from core.error_handlers.decorator import safe_async_execution
from app.bot.response import ServerDatabaseResponse
from core.logging.api import get_loggers


class AddExecutorService:
    def __init__(self, logging_data: LoggingData):
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ServerDatabaseResponse.ERROR_ADD_EXECUTOR.value,
        code=ServerDatabaseResponse.ERROR_ADD_EXECUTOR.name,
    )
    async def import_executor_from_path(
        self,
        executor_name: str,
        country: str,
        genres: List[str],
        base_path: Path,
        file_id: str,
        file_unique_id: str,
        get_audio_telegram: Callable[[Path, str], Awaitable[Message]],
        audio_extensions: Set[str],
        update_progress: Callable[[], Awaitable[bool]],
    ) -> Result:
        """
        Application service для сценария добавления исполнителя в базу данных.

        Отвечает за:
        - оркестрацию вызова AddExecutorAPI
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """
        albums = add_executor_api.parse_album(base_path=base_path)
        for parsed_album in albums:
            cancel: bool = await update_progress()
            if not cancel:
                return fail(
                    code=ServerDatabaseResponse.CANCEL_OPERATION.name,
                    message=ServerDatabaseResponse.CANCEL_OPERATION.value,
                )

            async with UnitOfWork() as uow:
                genres_list_executor: List[str] = await uow.genres.get_or_create_genres(
                    titles=genres
                )
                executor = await uow.executors.get_base_executor_by_name_and_country(
                    name=executor_name, country=country
                )
                if not executor:
                    executor = await uow.executors.create_base_executor(
                        name=executor_name,
                        genres=genres_list_executor,
                        country=country,
                        file_id=file_id,
                        file_unique_id=file_unique_id,
                    )
                executor_id = executor.id

                array_songs: List = []
                exists_album = await uow.albums.get_album_by_title(
                    executor_id=executor_id,
                    title=parsed_album.title,
                )
                if exists_album:
                    continue

                album = await uow.albums.create_album(
                    executor=executor,
                    title=parsed_album.title,
                    year=parsed_album.year,
                    photo_file_unique_id=settings.ALBUM_DEFAULT_PHOTO_UNIQUE_ID,
                    photo_file_id=settings.ALBUM_DEFAULT_PHOTO_FILE_ID,
                )

                for audio_path in parsed_album.path.iterdir():

                    if audio_path.suffix.lower() not in audio_extensions:
                        continue
                    try:

                        msg: Message = await get_audio_telegram(
                            audio_path,
                            parsed_album.title,
                        )
                        array_songs.append(
                            SongResponse(
                                file_id=msg.audio.file_id,
                                file_unique_id=msg.audio.file_unique_id,
                                title=audio_path.stem.lower(),
                            )
                        )
                    except Exception as err:
                        self.logging_data.warning_logger.warning(
                            "Не удалось загрузить трек",
                            extra={"path": audio_path, "error": str(err)},
                        )

                if array_songs:
                    await uow.songs.create_songs(
                        song_repsonse=array_songs,
                        album_id=album.id,
                    )
        return ok(
            data=ServerDatabaseResponse.SUCCESS_ADD_EXECUTOR.value.format(
                name=executor_name,
                country=country,
            )
        )

    async def chek_executor_exists(
        self,
        country: str,
        executor_name: str,
    ) -> Result:
        """
        Application service для сценария провекри существования в базе данных.

        Отвечает за:
        - оркестрацию вызова AddExecutorAPI
        - обработку ошибок
        - работу с базой данных
        - подготовку данных для handlers

        Не содержит логики взаимодействия с Telegram UI.
        """

        executor_exists = None
        async with UnitOfWork() as uow:
            executor = await uow.executors.get_base_executor_by_name_and_country(
                country=country, name=executor_name
            )
            if executor:
                genres: List[str] = [genre.title for genre in executor.genres]
                executor_exists = True
        if executor_exists:
            return ok(data=genres)
        return fail(code="NOT_EXECUTOR_EXISTS", message="Исполнителя нет в базе данных")


add_executor_service: AddExecutorService = AddExecutorService(
    logging_data=get_loggers(name=settings.NAME_FOR_LOG_FOLDER)
)
