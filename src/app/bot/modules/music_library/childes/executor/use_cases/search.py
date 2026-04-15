from typing import Optional

from application.use_cases.db.music_library.search_executor_by_name import (
    SearchExecutorName,
)
from domain.entities.validate import ExecutorValidator
from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.aiogram.fsm.data import UpdateAlbumYearData
from core.response.response_data import Result, LoggingData


async def process_serach_executor_by_name(
    logging_data: LoggingData,
    name: str,
    len_name: int,
    uwo: AbstractUnitOfWork,
    user_id: Optional[int],
) -> Result:
    result_name: Result = ExecutorValidator(name=name).validate_name()
    if not result_name.ok:
        return result_name
    name: str = result_name.data.casefold()

    result: Result = await SearchExecutorName(
        uow=uwo, logging_data=logging_data
    ).execute(
        name_lower=name,
        user_id=user_id,
        len_name=len_name,
    )
    return result
