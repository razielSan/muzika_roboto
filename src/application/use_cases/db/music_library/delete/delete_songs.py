from typing import List

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class DeleteSongsAlbum:
    def __init__(self, uow: AbstractUnitOfWork, logging_data: LoggingData):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        album_id: int,
        songs_id: List[int],
    ) -> Result:
        async with self.uow as uow:
            await uow.songs.delete_songs(album_id=album_id, songs_ids=songs_id)

        return ok(
            data=SuccessCode.DELETE_SONGS_SUCCESS,
            code=SuccessCode.DELETE_SONGS_SUCCESS,
        )
