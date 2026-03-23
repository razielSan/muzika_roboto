from typing import Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class UpdateCountryExecutor:
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
        country: str,
    ) -> Result:
        async with self.uow as uow:
            executor = await self.uow.executors.get_executor(
                user_id=user_id,
                executor_id=executor_id,
            )
            executor_exists: ExecutorDomain = await self.uow.executors.get_executor_by_name_lower_and_country_from_global_and_user(
                user_id=user_id, country=country, name_lower=executor.name_lower
            )
            if (
                executor_exists
            ):  # если исполнитель с таким именем и страной уже существует
                return fail(
                    code=ErorrCode.EXECUTOR_ALREADY_EXISTS.name,
                    message=ErorrCode.EXECUTOR_ALREADY_EXISTS.value,
                )

            executor: Optional[
                ExecutorDomain
            ] = await uow.executors.update_executor_country(
                executor_id=executor_id,
                user_id=user_id,
                country=country,
            )
            if not executor:
                return ok(
                    data=[], empty=True, code=NotFoundCode.EXECUTOR_NOT_FOUND.name
                )

        return ok(
            data=SuccessCode.UPDATE_EXECUTOR_COUNTRY_SUCCESS.value,
            code=SuccessCode.UPDATE_EXECUTOR_COUNTRY_SUCCESS.name,
        )
