from domain.entities.db.uow import UnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class UpdateTitleSongCollectionSongs:
    def __init__(self, uow: UnitOfWork, logging_data):
        self.uow: UnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        telegram: int,
        title: str,
        position: int,
    ) -> Result:
        async with self.uow as uow:
            user = await uow.users.get_user_by_telegram(telegram=telegram)
            if not user:  # если пользователя не существует
                return fail(
                    code=NotFoundCode.USER_NOT_FOUND.name,
                    message=NotFoundCode.USER_NOT_FOUND.value,
                )

            result_update = await uow.collection_songs.update_song_title(
                user_id=user.id, title=title, position=position
            )

            if not result_update:  # если нет песен в сборнике
                return ok(data=[], empty=True)

            return ok(data=result_update)
