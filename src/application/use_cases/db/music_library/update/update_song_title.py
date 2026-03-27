from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.song import Song as SongDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class UpdateSongTitle:
    def __init__(self, uow: AbstractUnitOfWork, logging_data: LoggingData):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        album_id: int,
        position: int,
        title: str,
    ) -> Result:
        async with self.uow as uow:
            song: Optional[SongDomain] = await uow.songs.update_title_song(
                position=position,
                album_id=album_id,
                title=title,
            )
            if not song:
                return ok(
                    code=NotFoundCode.SONG_POSITION_NOT_FOUND.name,
                    empty=True,
                    data=[],
                )

        return ok(
            data=SuccessCode.UPDATE_SONG_TITLE_SUCCESS,
            code=SuccessCode.UPDATE_SONG_TITLE_SUCCESS,
        )
