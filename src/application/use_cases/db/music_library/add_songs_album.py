from typing import List, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import SongResponse
from domain.entities.db.models.album import Album as AlbumDomain
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class AddSongsAlbum:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data,
    ):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        executor_id: int,
        album_id: int,
        songs: List[SongResponse],
    ) -> Result:

        async with self.uow as uow:
            album: Optional[AlbumDomain] = await uow.albums.get_album(
                executor_id=executor_id, album_id=album_id
            )
            if not album:
                return ok(data=[], empty=True, code=NotFoundCode.ALBUM_NOT_FOUND)

            position: Optional[int] = await uow.songs.get_last_postion_song(
                album_id=album.id
            )
            if not position:
                position = 1
            else:
                position += 1
            await uow.songs.add_songs(
                album_id=album.id, start_position=position, songs=songs
            )
        return ok(
            data=SuccessCode.ADD_SONGS_SUCCESS.value,
            code=SuccessCode.ADD_SONGS_SUCCESS.name,
        )
