from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import ExecutorSearchResponse
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class SearchExecutorName:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data,
    ):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        name_lower: str,
        user_id: Optional[int],
        len_name: int,
    ) -> Result:
        async with self.uow as uow:
            result_executors = []
            executors = []
            executor: Optional[
                ExecutorDomain
            ] = await uow.executors.get_executor_by_name_lower(
                user_id=user_id, name_lower=name_lower
            )
            if executor:
                result_executors.append(
                    ExecutorSearchResponse(
                        id=executor.id,
                        name=executor.name,
                        country=executor.country,
                        name_lower=executor.name_lower,
                    )
                )
                return ok(
                    data=result_executors,
                    code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
                )
            else:  # ищем по фильтру если не найдено по полному имени
                name: str = name_lower[0:len_name]
                executors = await uow.executors.get_executors_by_name_lower_filter_like(
                    user_id=user_id,
                    like=name,
                )
            if not executors:  # если не было найдено ни одного исполнителя
                return ok(
                    data=[],
                    empty=True,
                    code=NotFoundCode.EXECUTOR_NOT_FOUND.name,
                )

            for executor in executors:
                result_executors.append(
                    ExecutorSearchResponse(
                        id=executor.id,
                        name=executor.name,
                        country=executor.country,
                        name_lower=executor.name_lower,
                    )
                )

        return ok(
            data=result_executors,
            code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
        )
