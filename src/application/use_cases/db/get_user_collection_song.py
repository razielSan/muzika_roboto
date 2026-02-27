from domain.entities.db.uow import UnitOfWork
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail

from domain.errors.error_code import ErorrCode, NotFoundCode
from domain.entities.response import CollectionSongResponse, UserCollectionSongResponse


class GetUserCollectionSong:
    def __init__(self, uow: UnitOfWork, logging_data):
        self.uow: UnitOfWork = uow
        self.logging_data = logging_data
    
    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        telegram: int,
    ):
        collection_song_photo_file_id = None
        collection_song_photo_unique_id = None
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:  # если пользователя не существует
                return fail(
                    code=NotFoundCode.USER_NOT_FOUND.name,
                    message=NotFoundCode.USER_NOT_FOUND.value,
                )

            result_songs = await uow.collection_songs.get_all_songs(user_id=user.id)

            if not result_songs:  # если нет песен в сборнике
                return ok(data=[], empty=True)
            
            collection_song_photo_file_id: str = user.collection_song_photo_file_id
            collection_song_photo_unique_id: str = user.collection_song_photo_unique_id
            collection_songs = [
                CollectionSongResponse(
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                    title=song.title,
                    position=song.position,
                )
                for song in result_songs
            ]

        return ok(
            data=UserCollectionSongResponse(
                collection_songs=collection_songs,
                collection_song_photo_file_id=collection_song_photo_file_id,
                collection_song_photo_unique_id=collection_song_photo_unique_id,
            )
        )
