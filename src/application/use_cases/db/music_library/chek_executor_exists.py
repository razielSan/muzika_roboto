from typing import List, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.response import GenreResponse
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class ChekExecutorExists:
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
    async def execute(self, user_id: Optional[int], name: str, country: str) -> Result:

        async with self.uow as uow:
            name_lower: str = name.casefold()
            executor: ExecutorDomain = (
                await uow.executors.get_executor_by_name_lower_and_country(
                    user_id=user_id, name_lower=name_lower, country=country
                )
            )
            if not executor:
                return ok(
                    data=[],
                    empty=True,
                    code=NotFoundCode.EXECUTOR_NOT_FOUND,
                )
            genres: List[str] = [genre.title for genre in executor.genres]

        return ok(
            data=genres,
            code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
        )
