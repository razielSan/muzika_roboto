from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class UpdatePhotoExecutor:
    def __init__(self, uow: AbstractUnitOfWork, logging_data: LoggingData):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: Optional[int],
        executor_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Result:
        async with self.uow as uow:
            executor = await uow.executors.update_executor_photo_file_id(
                executoro_id=executor_id,
                user_id=user_id,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
            )
            if not executor:
                return ok(
                    data=[], empty=True, code=NotFoundCode.EXECUTOR_NOT_FOUND.name
                )

        return ok(
            data=SuccessCode.UPDATE_PHOTO_SUCCESS.value,
            code=SuccessCode.UPDATE_PHOTO_SUCCESS.name,
        )
