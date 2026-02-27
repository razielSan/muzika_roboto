from domain.entities.db.uow import UnitOfWork
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok

from domain.errors.error_code import ErorrCode


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
        user_id = None
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:
                user = await uow.users.create_user(name=name, telegram=telegram)
            user_id = user.id
        return ok(data=user_id)
