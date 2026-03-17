from typing import List

from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class CreateExecutor:
    def __init__(
        self,
        uow: AbstractUnitOfWork,
        logging_data,
    ):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        name: str,
        country: str,
        genres_executor: List[str],
        user_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Result:

        async with self.uow as uow:
            genres_list_executor: List[str] = await uow.genres.get_or_create_genres(
                titles=genres_executor
            )
            name_lower: str = name.casefold()
            executor = await uow.executors.get_executor_by_name_lower_and_country(
                user_id=user_id, name_lower=name_lower, country=country
            )
            if executor:
                return fail(
                    code=ErorrCode.EXECUTOR_ALREADY_EXISTS.name,
                    message=ErorrCode.EXECUTOR_ALREADY_EXISTS.value,
                )
            executor = await uow.executors.create_executor(
                user_id=user_id,
                name=name,
                country=country,
                photo_file_id=photo_file_id,
                photo_file_unique_id=photo_file_unique_id,
                genres=genres_list_executor,
            )

        return ok(
            data=SuccessCode.ADD_EXECUTOR_SUCCESS.value,
            code=SuccessCode.ADD_EXECUTOR_SUCCESS.name,
        )
