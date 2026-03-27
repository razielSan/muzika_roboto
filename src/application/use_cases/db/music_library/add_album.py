from typing import List, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import SongResponse
from domain.entities.db.models.album import Album as AlbumDomain
from domain.errors.error_code import ErorrCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class AddAlbumExecutor:
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
        executor_id: int,
        title: str,
        year: int,
        photo_file_id: str,
        photo_file_unique_id: str,
        songs: List[SongResponse],
    ) -> Result:

        async with self.uow as uow:
            exists_album: Optional[
                AlbumDomain
            ] = await self.uow.albums.get_album_by_title(
                executor_id=executor_id, title=title
            )
            if exists_album:
                return fail(
                    message=ErorrCode.ALBUM_ALREADY_EXISTS.value,
                    code=ErorrCode.ALBUM_ALREADY_EXISTS.name,
                )

            album: AlbumDomain = await uow.albums.create_album(
                executor_id=executor_id,
                title=title,
                year=year,
                photo_file_unique_id=photo_file_unique_id,
                photo_file_id=photo_file_id,
            )

            position: Optional[int] = await uow.songs.get_last_postion_song(
                album_id=album.id
            )
            if not position:
                position = 1
            else:
                position += 1

            await uow.songs.add_songs(
                album_id=album.id, start_position=position, songs=songs
            )
        return ok(
            data=SuccessCode.ADD_AlBUM_SUCCESS.value,
            code=SuccessCode.ADD_AlBUM_SUCCESS.name,
        )
