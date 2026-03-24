from typing import Optional, List

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.db.models.executor import Executor as ExecutorDomain
from domain.entities.db.models.genre import Genre as GenreDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result, LoggingData


class UpdateGenreExecutor:
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
        genres: List[str],
    ) -> Result:
        async with self.uow as uow:
            update_genres: List[GenreDomain] = await uow.genres.get_or_create_genres(
                titles=genres
            )
            executor: Optional[
                ExecutorDomain
            ] = await uow.executors.update_executor_genres(
                executor_id=executor_id, genres=update_genres, user_id=user_id
            )
            if not executor:
                return ok(
                    data=[], empty=True, code=NotFoundCode.EXECUTOR_NOT_FOUND.name
                )

        return ok(
            data=SuccessCode.UPDATE_GENRES_SUCCESS.value,
            code=SuccessCode.UPDATE_GENRES_SUCCESS.name,
        )
