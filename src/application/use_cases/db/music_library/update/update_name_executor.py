from typing import Optional, List

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class UpdateNameExecutor:
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
        name: str,
        country: str,
    ) -> Result:
        async with self.uow as uow:
            curremt_page_executor: int = 1

            name_lower: str = name.casefold()
            executor_exists: Optional[
                ExecutorDomain
            ] = await uow.executors.get_executor_by_name_lower_and_country_from_global_and_user(
                user_id=user_id,
                name_lower=name_lower,
                country=country,
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
            ] = await uow.executors.update_executor_name(
                executor_id=executor_id, user_id=user_id, name=name
            )

            if not executor:  # Если исполнитель не был найден
                return ok(
                    data=curremt_page_executor,
                    empty=True,
                    code=NotFoundCode.EXECUTOR_NOT_FOUND.name,
                )

            executors: List[
                ExecutorDomain
            ] = await self.uow.users.get_library_executors(user_id=user_id)
            for page, executor in enumerate(executors, start=1):
                if executor.name == name and executor.country == country:
                    curremt_page_executor = page

        return ok(
            data=curremt_page_executor,
            code=SuccessCode.UPDATE_NAME_SUCCESS.name,
        )
