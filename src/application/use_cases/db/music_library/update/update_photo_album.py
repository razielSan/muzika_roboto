from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.db.models.album import Album as DomanALbum
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class UpdatePhotoAlbum:
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
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Result:
        async with self.uow as uow:
            album: Optional[DomanALbum] = await uow.albums.update_photo_file_id(
                executor_id=executor_id,
                album_id=album_id,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )
            if not album:
                return ok(data=[], empty=True, code=NotFoundCode.ALBUM_NOT_FOUND.name)

        return ok(
            data=SuccessCode.UPDATE_PHOTO_SUCCESS.value,
            code=SuccessCode.UPDATE_PHOTO_SUCCESS.name,
        )
