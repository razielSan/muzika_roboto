from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from domain.entities.response import (
    CollectionSongsResponse,
    UserCollectionSongsResponse,
)
from domain.entities.db.models.user import User as UserDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class GetUserCollectionSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user: UserDomain,
    ) -> Result:
        async with self.uow as uow:
            result_songs = await uow.collection_songs.get_all_songs(user_id=user.id)

            if not result_songs:  # если нет песен в сборнике
                return ok(
                    data=UserCollectionSongsResponse(collection_songs=[]),
                    empty=True,
                    code=NotFoundCode.SONGS_NOT_FOUND.name,
                )

            collection_songs = [
                CollectionSongsResponse(
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                    title=song.title,
                    position=song.position,
                    id=song.id,
                )
                for song in result_songs
            ]

        return ok(
            data=UserCollectionSongsResponse(
                collection_songs=collection_songs,
                collection_songs_photo_file_id=user.collection_songs_photo_file_id,
                collection_songs_photo_file_unique_id=user.collection_songs_photo_file_unique_id,
            ),
            code=SuccessCode.GET_SONGS_SUCCESS.name,
        )
