from typing import List, Optional

from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.db.models.executor import Executor as DomainExecutor
from domain.errors.error_code import ErorrCode, SuccessCode
from domain.entities.validate import ExecutorValidator
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
        # Проверка входящих данных
        validate_executor = ExecutorValidator(
            name=name, country=country, genres=genres_executor
        )
        validate_name = validate_executor.validate_name()
        if not validate_name.ok:
            return validate_name
        validate_country = validate_executor.validate_country()
        if not validate_country.ok:
            return validate_country
        validate_genres = validate_executor.validate_genres()
        if not validate_genres.ok:
            return validate_genres

        executor_id = None
        async with self.uow as uow:
            genres_list_executor: List[str] = await uow.genres.get_or_create_genres(
                titles=genres_executor
            )
            name_lower: str = name.casefold()
            executor_exists: Optional[
                DomainExecutor
            ] = await uow.executors.get_executor_by_name_lower_and_country_from_global_and_user(
                user_id=user_id,
                name_lower=name_lower,
                country=country,
            )
            if executor_exists:
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
            executor_id = executor.id

        return ok(
            data=executor_id,
            code=SuccessCode.ADD_EXECUTOR_SUCCESS.name,
        )
