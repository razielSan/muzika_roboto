from domain.entities.db.uow import AbstractUnitOfWork
from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result, LoggingData


class DeleteUser:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data: LoggingData = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: int,
    ) -> Result:
        async with self.uow as uwo:
            result = await uwo.users.delete_user(user_id=user_id)
            if not result:
                return fail(
                    code=NotFoundCode.USER_NOT_FOUND.name,
                    message=NotFoundCode.USER_NOT_FOUND.value,
                )

        return ok(code=SuccessCode.DELETE_USER_SUCCESS.name, data=True)
