from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import CollectionSongsResponse
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class GetSongCollectionSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: int,
        song_id: int,
    ) -> Result:
        async with self.uow as uow:
            song = await uow.collection_songs.get_song(
                user_id=user_id,
                song_id=song_id,
            )
            if not song:
                return fail(
                    code=NotFoundCode.SONGS_NOT_FOUND.name,
                    message=NotFoundCode.SONGS_NOT_FOUND.value,
                )
            song_response: CollectionSongsResponse = CollectionSongsResponse(
                file_id=song.file_id,
                file_unique_id=song.file_unique_id,
                title=song.title,
                position=song.position,
            )

        return ok(data=song_response, code=SuccessCode.GET_SONGS_SUCCESS.name)
