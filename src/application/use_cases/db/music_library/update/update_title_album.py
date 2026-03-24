from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.album import Album as AlbumDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class UpdateAlumbTitle:
    def __init__(self, uow: AbstractUnitOfWork, logging_data: LoggingData):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        album_id: int,
        executor_id: int,
        title: str,
    ) -> Result:
        async with self.uow as uow:
            exists_album: Optional[
                AlbumDomain
            ] = await self.uow.albums.get_album_by_title(
                executor_id=executor_id,
                title=title,
            )
            if exists_album:
                return fail(
                    code=ErorrCode.ALBUM_ALREADY_EXISTS.name,
                    message=ErorrCode.ALBUM_ALREADY_EXISTS.value,
                )

            album: Optional[AlbumDomain] = await self.uow.albums.update_title(
                executor_id=executor_id, album_id=album_id, title=title
            )
            if not album:
                return ok(data=[], empty=True, code=NotFoundCode.ALBUM_NOT_FOUND.name)

        return ok(
            data=SuccessCode.UPDATE_ALBUM_TITLE_SUCCESS.value,
            code=SuccessCode.UPDATE_ALBUM_TITLE_SUCCESS.name,
        )
