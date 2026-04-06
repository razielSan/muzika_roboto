from typing import List, Optional, Callable, Set, Awaitable
from pathlib import Path

from aiogram.types import Message

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import SongResponse
from domain.entities.db.models.album import Album as AlbumDomain
from domain.errors.error_code import ErorrCode, SuccessCode
from infrastructure.utils.parsed import parse_album
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class ImportExecutorFromPath:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        executor_name: str,
        country: str,
        genres: List[str],
        base_path: Path,
        file_id: str,
        file_unique_id: str,
        get_audio_telegram: Callable[[Path, str], Awaitable[Message]],
        audio_extensions: Set[str],
        album_default_photo_file_id: str,
        album_defautl_photo_file_unique_id: str,
        update_progress: Callable[[], Awaitable[bool]],
    ) -> Result:

        albums = parse_album(base_path=base_path)
        for parsed_album in albums:
            cancel: bool = await update_progress()
            if not cancel:
                return fail(
                    code=ErorrCode.CANCEL_ERROR.name,
                    message=ErorrCode.CANCEL_ERROR.value,
                )

            async with self.uow as uow:
                genres_list_executor = await uow.genres.get_or_create_genres(
                    titles=genres
                )
                name_lower: str = executor_name.casefold()
                executor = await uow.executors.get_executor_by_name_lower_and_country(
                    user_id=None,
                    name_lower=name_lower,
                    country=country,
                )
                if not executor:
                    executor = await self.uow.executors.create_executor(
                        user_id=None,
                        name=executor_name,
                        country=country,
                        genres=genres_list_executor,
                        photo_file_id=file_id,
                        photo_file_unique_id=file_unique_id,
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
                    executor_id=executor_id,
                    title=parsed_album.title,
                    year=parsed_album.year,
                    photo_file_unique_id=album_defautl_photo_file_unique_id,
                    photo_file_id=album_default_photo_file_id,
                )

                for audio_path in parsed_album.path.iterdir():

                    if audio_path.suffix.lower() not in audio_extensions:
                        continue
                    try:

                        msg: Message = await get_audio_telegram(
                            audio_path,
                            parsed_album.title,
                            parsed_album.year,
                        )
                        file_name: str = audio_path.parts[-1]
                        if msg.audio:
                            array_songs.append(
                                SongResponse(
                                    file_id=msg.audio.file_id,
                                    file_unique_id=msg.audio.file_unique_id,
                                    title=file_name,
                                )
                            )
                        if msg.voice:
                            array_songs.append(
                                SongResponse(
                                    file_id=msg.voice.file_id,
                                    file_unique_id=msg.voice.file_unique_id,
                                    title=file_name,
                                )
                            )

                    except Exception as err:
                        self.logging_data.warning_logger.warning(
                            "Не удалось загрузить трек",
                            extra={"path": audio_path, "error": str(err)},
                        )

                if array_songs:
                    await uow.songs.add_songs(
                        songs=array_songs,
                        album_id=album.id,
                    )

        return ok(
            data=SuccessCode.ADD_EXECUTOR_SUCCESS.value,
            code=SuccessCode.ADD_AlBUM_SUCCESS.name,
        )
