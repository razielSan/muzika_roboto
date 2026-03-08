from typing import List, Sequence, Union, Callable

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from domain.entities.response import ExecutorPageResponse, AlbumResponse
from domain.entities.db.models.executor import Executor as ExecutorDomain
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class GetExecutorWihtAlbums:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: Union[int, None],
        current_page=1,
    ) -> Result:
        async with self.uow as uow:
            executors: Sequence[ExecutorDomain] = await uow.executors.get_all_executors(
                user_id=user_id
            )
            if not executors:  # если нет исполнителей
                return ok(
                    data=None,
                    empty=True,
                    code=NotFoundCode.EXECUTORS_NOT_FOUND.name,
                )

            executor: ExecutorDomain = executors[current_page - 1]
            total_pages: int = len(executors)
            genres: List[str] = [genre.title for genre in executor.genres]
            executor_albums = []
            if executor.albums:  # если есть альбомы
                executor_albums: List[AlbumResponse] = [
                    AlbumResponse(
                        id=album.id,
                        executor_id=album.executor_id,
                        year=album.year,
                        title=album.title,
                    )
                    for album in executor.albums
                ]

            response_executor: ExecutorPageResponse = ExecutorPageResponse(
                id=executor.id,
                name=executor.name,
                country=executor.country,
                user_id=executor.user_id,
                photo_file_id=executor.photo_file_id,
                photo_file_unique_id=executor.photo_file_unique_id,
                current_page=current_page,
                genres=genres,
                albums=executor_albums,
                total_pages=total_pages,
            )

        return ok(
            data=response_executor,
            code=SuccessCode.GET_EXECUTORS_SUCCESS.name,
        )
