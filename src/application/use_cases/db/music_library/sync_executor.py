from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class SyncExecutorLibrary:
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
        executor_id: int,
        user_id: int,
    ) -> Result:

        async with self.uow as uow:
            user_executor: bool = await uow.user_executors.exists(
                executor_id=executor_id,
                user_id=user_id,
            )
            if user_executor:
                return fail(
                    code=ErorrCode.USER_EXECUTOR_ALREADY_EXISTS.name,
                    message=ErorrCode.USER_EXECUTOR_ALREADY_EXISTS.value,
                )
            await uow.user_executors.add(user_id=user_id, executor_id=executor_id)
        return ok(
            data=SuccessCode.SYNC_EXECUTOR_SUCCESS.value,
            code=SuccessCode.SYNC_EXECUTOR_SUCCESS.name,
        )
