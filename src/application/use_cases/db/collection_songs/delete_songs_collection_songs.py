from typing import List
from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class DeleteSongsCollectionSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(self, telegram: int, list_ids: List[int]) -> Result:

        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:  # если пользователя не существует
                return fail(
                    code=NotFoundCode.USER_NOT_FOUND.name,
                    message=NotFoundCode.USER_NOT_FOUND.value,
                )

            await self.uow.collection_songs.delete_songs(
                user_id=user.id,
                list_ids=list_ids,
            )
        return ok(
            data=SuccessCode.DELETE_SONGS_SUCCESS.name,
            code=SuccessCode.DELETE_SONGS_SUCCESS.name,
        )
