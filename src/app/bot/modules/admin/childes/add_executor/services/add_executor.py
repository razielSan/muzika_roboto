from typing import List, Callable, Set
from pathlib import Path

from aiogram.types import Message
from sqlalchemy.exc import IntegrityError

from app.bot.modules.admin.childes.add_executor.api.add_executor import api_add_executor
from app.bot.settings import settings
from app.bot.db.uow import UnitOfWork
from app.bot.db.response import SongResponse
from core.error_handlers.helpers import ok, fail
from core.error_handlers.format import format_errors_message
from core.response.response_data import LoggingData
from core.response.messages import messages



class ServiceAddExecutor:
    async def import_executor_from_path(
        self,
        telegram: int,
        user_name: str,
        executor_name: str,
        country: str,
        genres: List[str],
        base_path: Path,
        file_id: str,
        file_unique_id: str,
        get_audio_telegram: Callable[[Path], Message],
        logging_data: LoggingData,
        audio_extensions: Set,
    ):
        try:
            albums = api_add_executor.parse_album(base_path=base_path)
            async with UnitOfWork() as uow:
                user = await uow.users.get_user_by_telegram(
                    telegram=telegram,
                )
                if not user:
                    user = await uow.users.create_user(
                        telegram=telegram, name=user_name
                    )
                genres = await uow.genres.get_or_create_genres(titles=genres)
                executor = await uow.executors.get_executor_by_name_and_country(
                    user_id=user.id, name=executor_name, country=country
                )
                if not executor:
                    executor = await uow.executors.create_executor(
                        name=executor_name,
                        user=user,
                        genres=genres,
                        country=country,
                        file_id=file_id,
                        file_unique_id=file_unique_id,
                    )

                for parsed_album in albums:
                    array_songs = []
                    exists_album = await uow.albums.get_album_by_title(
                        executor_id=executor.id,
                        title=parsed_album.title,
                    )
                    if exists_album:
                        continue

                    album = await uow.albums.create_album(
                        executor=executor,
                        title=parsed_album.title,
                        year=parsed_album.year,
                        photo_file_unique_id=settings.ALBUM_DEFAULT_PHOTO_UNIQUE_ID,
                        photo_file_id=settings.ALBUM_DEFAULT_PHOTO_UNIQUE_ID,
                    )

                    position = 0
                    for audio_path in parsed_album.path.iterdir():

                        if audio_path.suffix.lower() not in audio_extensions:
                            continue
                        try:
                            msg: Message = await get_audio_telegram(
                                audio_path=audio_path
                            )
                            position += 1
                            array_songs.append(
                                SongResponse(
                                    file_id=msg.audio.file_id,
                                    file_unique_id=msg.audio.file_unique_id,
                                    position=position,
                                    title=audio_path.stem,
                                )
                            )
                        except Exception as err:
                            logging_data.warning_logger.warning(
                                "Не удалось загрузить трек",
                                extra={"path": audio_path, "error": str(err)},
                            )
                            
                    if array_songs:
                        await uow.songs.create_songs(
                            song_repsonse=array_songs,
                            album=album,
                        )

            return ok(data=f"{executor_name}: {country} с альбомами был создан")
        except Exception as err:
            logging_data.error_logger.exception(
                msg=format_errors_message(
                    name_router=logging_data.router_name,
                    function_name=self.import_executor_from_path.__name__,
                    error_text=str(err),
                )
            )
            return fail(
                code="ADD_EXECUTOR_ERROR",
                message=messages.SERVER_ERROR,
            )


service_add_executor = ServiceAddExecutor()
