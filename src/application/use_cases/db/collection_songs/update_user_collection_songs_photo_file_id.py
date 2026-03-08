from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class UpdateUserCollectionSongsPhotoFileId:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        photo_file_id: str,
        photo_file_unique_id: str,
        user_id: int,
    ) -> Result:
        async with self.uow as uow:
            await uow.users.update_collection_songs_photo_file_id(
                user_id=user_id,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )
        return ok(data=user_id, code=SuccessCode.UPDATE_PHOTO_SUCCESS.name)
