from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, SuccessCode
from domain.entities.validate import UserValidator
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok


class GetOrCreateUser:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
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
        # Проверка входящих данных
        validator = UserValidator(name=name, telegram=telegram)
        validate_name = validator.validate_name()
        if not validate_name.ok:
            return validate_name
        validate_telegram = validator.validate_telegram()
        if not validate_telegram.ok:
            return validate_telegram

        user_id = None
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:
                user = await uow.users.create_user(name=name, telegram=telegram)
            user_id = user.id
        return ok(data=user_id, code=SuccessCode.ADD_USER_SUCCESS.name)
