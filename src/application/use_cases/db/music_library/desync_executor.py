from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok
from core.response.response_data import Result


class DesyncExecutorLibrary:
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
            await uow.user_executors.delete(user_id=user_id, executor_id=executor_id)

            user_executors = await self.uow.users.get_library_executors(user_id=user_id)
            if not user_executors:  # если не осталось исполнителей
                return ok(
                    data=[],
                    code=NotFoundCode.USER_EXECUTOR_NOT_FOND.name,
                    empty=True,
                )

        return ok(
            data=SuccessCode.DESYNC_EXECUTOR_SUCCESS.value,
            code=SuccessCode.DESYNC_EXECUTOR_SUCCESS.name,
        )
