from typing import Union

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.album import Album as AlbumDomain
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.response import AlbumPageResponse, SongResponse
from domain.entities.validate import AlbumValidator
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class GetAlbumWithSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: Union[int, None],
        executor_id: int,
        album_id: int,
        album_position=0,
        current_page_executor=1,
        is_global_executor=True,
    ) -> Result:
        
        # ПРоверка входящих значений
        vaidator = AlbumValidator(
            album_id=album_id,
            executor_id=executor_id,
            user_id=user_id,
        )
        validate_user_id = vaidator.validate_user_id()
        if not validate_user_id.ok:
            return validate_user_id

        validate_album_id = vaidator.validate_album_id()
        if not validate_album_id.ok:
            return validate_album_id

        validate_executor_id = vaidator.validate_executor_id()
        if not validate_executor_id.ok:
            return validate_executor_id

        async with self.uow as uow:
            if user_id:  # пользовательская библиотека(берем исполнителя по execitor_id)
                executor: ExecutorDomain = (
                    await uow.executors.get_executor_by_user_library(
                        executor_id=executor_id
                    )
                )
            if not user_id:  # глобальная(user_id всегда None)
                executor: ExecutorDomain = await uow.executors.get_executor(
                    user_id=None,
                    executor_id=executor_id,
                )
            album: AlbumDomain = await uow.albums.get_album(
                executor_id=executor.id, album_id=album_id
            )
            if not album:
                return ok(data=[], empty=True, code=NotFoundCode.ALBUM_NOT_FOUND.name)
            songs = [
                SongResponse(
                    id=song.id,
                    title=song.title,
                    position=song.position,
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                    album_id=song.album_id,
                )
                for song in album.songs
            ]
            response_album = AlbumPageResponse(
                user_id=user_id,
                id=album.id,
                executor_id=album.executor_id,
                year=album.year,
                photo_file_id=album.photo_file_id,
                photo_file_unique_id=album.photo_file_unique_id,
                songs=songs,
                title=album.title,
                current_page_executor=current_page_executor,
                album_position=album_position,
                is_global_executor=is_global_executor,
            )
        return ok(data=response_album, code=SuccessCode.GET_ALBUMS_SUCCESS.name)
