from typing import List, Union, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class GetExecutorPage:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: Union[int, None],
        executor_id: int,
    ) -> Result:
        async with self.uow as uow:
            current_page_executor: int = 1
            executor: Optional[ExecutorDomain] = await uow.executors.get_executor(
                user_id=user_id,
                executor_id=executor_id,
            )
            if not executor:
                return ok(
                    code=NotFoundCode.EXECUTOR_NOT_FOUND.name,
                    empty=True,
                    data=current_page_executor,
                )
            all_executors: List[ExecutorDomain] = await uow.executors.get_all_executors(
                user_id=user_id,
            )

            for index, executor in enumerate(all_executors, start=1):
                if executor.id == executor_id:
                    current_page_executor = index
                    break
        return ok(
            data=current_page_executor,
            code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
        )
