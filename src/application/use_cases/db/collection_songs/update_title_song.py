from domain.entities.db.uow import AbstractUnitOfWork
from domain.errors.error_code import ErorrCode, NotFoundCode, SuccessCode
from core.error_handlers.decorator import safe_async_execution
from core.error_handlers.helpers import ok, fail
from core.response.response_data import Result


class UpdateTitleSongCollectionSongs:
    def __init__(self, uow: AbstractUnitOfWork, logging_data):
        self.uow: AbstractUnitOfWork = uow
        self.logging_data = logging_data

    @safe_async_execution(
        message=ErorrCode.UNKNOWN_ERROR.value, code=ErorrCode.UNKNOWN_ERROR.name
    )
    async def execute(
        self,
        user_id: int,
        title: str,
        position: int,
    ) -> Result:
        async with self.uow as uow:

            result_update = await uow.collection_songs.update_song_title(
                user_id=user_id, title=title, position=position
            )

            if not result_update:  # если нет песен в сборнике
                return ok(
                    data=[],
                    empty=True,
                    code=NotFoundCode.SONG_POSITION_NOT_FOUND.name,
                )

        return ok(
            data=SuccessCode.UPDATE_SONG_TITLE_SUCCESS.value,
            code=SuccessCode.UPDATE_SONG_TITLE_SUCCESS.name,
        )
