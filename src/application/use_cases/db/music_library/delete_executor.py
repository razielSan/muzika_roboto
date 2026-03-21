from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class DeleteExecutor:
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
    ) -> Result:
        async with self.uow as uow:
            executor: ExecutorDomain = await uow.executors.delete_executor(
                user_id=user_id,
                executor_id=executor_id,
            )
            if not executor:
                return ok(data=[], code=NotFoundCode.EXECUTOR_NOT_FOUND.name)

        return ok(
            data=SuccessCode.DELETE_EXECUTOR_SUCCESS.value,
            code=SuccessCode.DELETE_EXECUTOR_SUCCESS.name,
        )
