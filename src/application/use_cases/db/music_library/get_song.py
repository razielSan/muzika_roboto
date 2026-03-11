from typing import Union

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.album import Album as AlbumDomain
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.response import AlbumPageResponse, SongResponse
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class GetSongAlbum:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        album_id: int,
        song_id: int,
    ) -> Result:

        async with self.uow as uow:
            song = await uow.songs.get_song(album_id=album_id, song_id=song_id)
            if not song:
                return ok(
                    data=[],
                    empty=True,
                    code=NotFoundCode.SONG_NOT_FOUND.name,
                )

            song_response = SongResponse(
                id=song.id,
                title=song.title,
                album_id=song.album_id,
                position=song.position,
                file_id=song.file_id,
                file_unique_id=song.file_unique_id,
            )
        return ok(data=song_response, code=SuccessCode.GET_SONG_SUCCESS.name)
