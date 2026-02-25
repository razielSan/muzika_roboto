from domain.entities.db.uow import UnitOfWork
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail

from domain.errors.error_code import ErorrCode, NotFoundCode


class GetUserCollectionSong:
    def __init__(self, uow: UnitOfWork, logging_data):
        self.uow: UnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        telegram: int,
    ):
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:  # если пользователь не существует
                return fail(
                    code=NotFoundCode.USER_NOT_FOUND.name,
                    message=NotFoundCode.USER_NOT_FOUND.value,
                )

            collection_song = await uow.collection_songs.get_all_songs(user_id=user.id)

            if not collection_song:  # если нет песен в сборнике
                return ok(data=[], empty=True)

            return ok(data=collection_song)
