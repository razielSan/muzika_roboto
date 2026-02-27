from typing import List

from domain.entities.db.uow import UnitOfWork
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from domain.errors.error_code import ErorrCode, SuccessCode
from domain.entities.response import CollectionSongResponse


class AddSongsToCollectionSong:
    def __init__(self, uow: UnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_name: str,
        telegram: int,
        collection_songs: List[CollectionSongResponse],
    ):
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:
                user = await uow.users.create_user(name=user_name, telegram=telegram)

            poisition = await uow.collection_songs.get_last_poistion_song(
                user_id=user.id,
            )
            if poisition:
                poisition += 1
            if not poisition:
                poisition = 1

            songs = await uow.collection_songs.add_songs(
                collection_songs=collection_songs,
                start_position=poisition,
                user_id=user.id,
            )

        return ok(data=SuccessCode.SUCCESS_COLLECTION_SONG.name)
