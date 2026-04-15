from application.use_cases.db.music_library.update.update_year_album import (
    UpdateAlumbYear,
)
from domain.entities.validate import AlbumValidator
from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.aiogram.fsm.data import UpdateAlbumYearData
from core.response.response_data import Result, LoggingData


async def process_update_album_year(
    state_data: UpdateAlbumYearData,
    logging_data: LoggingData,
    number: str,
    uwo: AbstractUnitOfWork,
) -> Result:
    result_year: Result = AlbumValidator(year=number).validate_year()
    if not result_year.ok:  # если год был указан не верно
        return result_year
    year: int = result_year.data

    result: Result = await UpdateAlumbYear(logging_data=logging_data, uow=uwo,).execute(
        executor_id=state_data.executor_id,
        album_id=state_data.album_id,
        year=year,
    )
    return result
