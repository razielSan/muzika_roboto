from typing import Union

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.album import Album as AlbumDomain
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.response import AlbumPageResponse, SongResponse
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class GetAlbumWithSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: Union[int, None],
        executor_id: int,
        album_id: int,
        album_position=0,
        current_page_executor=1,
    ) -> Result:
        async with self.uow as uow:
            executor: ExecutorDomain = await uow.executors.get_executor(
                user_id=user_id, executor_id=executor_id
            )
            album: AlbumDomain = await uow.albums.get_album(
                executor_id=executor.id, album_id=album_id
            )
            if not album:
                return ok(data=[], empty=True, code=NotFoundCode.ALBUM_NOT_FOUND.name)
            songs = [
                SongResponse(
                    id=song.id,
                    title=song.title,
                    position=song.position,
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                    album_id=song.album_id,
                )
                for song in album.songs
            ]
            response_album = AlbumPageResponse(
                user_id=user_id,
                id=album.id,
                executor_id=album.executor_id,
                year=album.year,
                photo_file_id=album.photo_file_id,
                photo_file_unique_id=album.photo_file_unique_id,
                songs=songs,
                title=album.title,
                current_page_executor=current_page_executor,
                album_position=album_position,
            )
        return ok(data=response_album, code=SuccessCode.GET_ALBUMS_SUCCESS.name)
