from typing import List

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode
from domain.entities.response import CollectionSongsResponse
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class AddSongsToCollectionSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: int,
        collection_songs: List[CollectionSongsResponse],
    ) -> Result:
        async with self.uow as uow:

            poisition = await uow.collection_songs.get_last_poistion_song(
                user_id=user_id,
            )
            if poisition:
                poisition += 1
            if not poisition:
                poisition = 1

            songs = await uow.collection_songs.add_songs(
                collection_songs=collection_songs,
                start_position=poisition,
                user_id=user_id,
            )

        return ok(
            data=SuccessCode.ADD_SONGS_SUCCESS.name,
            code=SuccessCode.ADD_SONGS_SUCCESS.name,
        )
