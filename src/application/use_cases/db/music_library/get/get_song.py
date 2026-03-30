from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.song import Song as SongDomain
from domain.entities.response import SongResponse
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class GetSongAlbum:
    def __init__(self, uow: AbstractUnitOfWork, logging_data: LoggingData):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        album_id: int,
        song_id: int,
    ) -> Result:

        async with self.uow as uow:
            song: SongDomain = await uow.songs.get_song(
                album_id=album_id, song_id=song_id
            )
            if not song:
                return ok(
                    data=[],
                    empty=True,
                    code=NotFoundCode.SONG_NOT_FOUND.name,
                )

            song_response: SongResponse = SongResponse(
                id=song.id,
                title=song.title,
                album_id=song.album_id,
                position=song.position,
                file_id=song.file_id,
                file_unique_id=song.file_unique_id,
            )
        return ok(data=song_response, code=SuccessCode.GET_SONG_SUCCESS.name)
