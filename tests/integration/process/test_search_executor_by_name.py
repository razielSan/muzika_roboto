import pytest

from app.bot.modules.music_library.childes.executor.use_cases.search import (
    process_serach_executor_by_name,
)
from application.use_cases.db.music_library.create_executor import CreateExecutor
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode


@pytest.mark.integration
@pytest.mark.asyncio
async def test_succes(uwo, fake_logging_data):

    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user_id = None

    await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=name_executor,
        country=country,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
        genres_executor=genres,
    )
    result = await process_serach_executor_by_name(
        logging_data=fake_logging_data,
        name=name_executor,
        len_name=5,
        uwo=uwo,
        user_id=user_id,
    )
    assert result.code == SuccessCode.GET_EXECUTORS_SUCCESS.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_executor_not_found(uwo, fake_logging_data):

    name_executor: str = "executor"
    user_id = None

    result = await process_serach_executor_by_name(
        logging_data=fake_logging_data,
        name=name_executor,
        len_name=5,
        uwo=uwo,
        user_id=user_id,
    )
    assert result.code == NotFoundCode.EXECUTOR_NOT_FOUND.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_executor_name(uwo, fake_logging_data):

    name_executor: str = 123
    user_id = None

    result = await process_serach_executor_by_name(
        logging_data=fake_logging_data,
        name=name_executor,
        len_name=5,
        uwo=uwo,
        user_id=user_id,
    )
    assert result.error.code == ErorrCode.INVALID_EXECUTOR_NAME.name
