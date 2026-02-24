from domain.entities.db.uow import UnitOfWork
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail

from domain.errors.error_code import ErorrCode, ExistsErrorCode
from domain.exceptions.db.user import UserAlreadyExists


class GetOrCreateUser:
    def __init__(self, uow: UnitOfWork, logging_data):
        self.uow = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        name: str,
        telegram: int,
    ):
        async with self.uow as uow:
            try:
                user = await uow.users.get_user_by_telegram(telegram=telegram)
                if not user:
                    user = await uow.users.create_user(name=name, telegram=telegram)
                return ok(data=user)
            except UserAlreadyExists:
                return fail(
                    code=ExistsErrorCode.USER_ALREADY_EXISTS.name,
                    message="Пользователь уже существует",
                )
