from application.use_cases.db.user.delete_user import DeleteUser
from domain.entities.validate import UserValidator
from domain.entities.db.uow import AbstractUnitOfWork
from core.response.response_data import Result, LoggingData


async def process_delete_user(
    logging_data: LoggingData,
    uwo: AbstractUnitOfWork,
    user_id: str,
) -> Result:
    result_validate: Result = UserValidator(id=user_id).validate_id()
    if not result_validate.ok:
        return result_validate
    user_id: int = result_validate.data

    result: Result = await DeleteUser(uow=uwo, logging_data=logging_data).execute(
        user_id=user_id
    )
    return result
