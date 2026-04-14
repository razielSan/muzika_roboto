from typing import List, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.response import ExecutorSearchResponse
from domain.errors.error_code import ErorrCode, SuccessCode
from domain.entities.db.models.genre import Genre as GenreDomain
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class SearchExecutorGenre:
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
        title: str,
        user_id: Optional[int],
    ) -> Result:

        async with self.uow as uow:
            genre: GenreDomain = await uow.genres.get_genre(title=title)
            if not genre:
                return fail(
                    code=ErorrCode.GENRE_DOES_NOT_EXIST.name,
                    message=ErorrCode.GENRE_DOES_NOT_EXIST.value,
                )
            all_executors: List[ExecutorDomain] = genre.executors
            executors: List[ExecutorSearchResponse] = []
            for executor in all_executors:
                if executor.user_id == user_id:
                    executors.append(
                        ExecutorSearchResponse(
                            id=executor.id,
                            name=executor.name,
                            country=executor.country,
                            name_lower=executor.name_lower,
                        )
                    )
            executors.sort(key=lambda executor: executor.name_lower)

        return ok(
            data=executors,
            code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
        )
