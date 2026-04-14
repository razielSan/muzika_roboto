import pytest

from application.use_cases.db.user.get_or_create_user import GetOrCreateUser
from domain.errors.error_code import ErorrCode


@pytest.mark.integration
@pytest.mark.asyncio
async def test_success_get_or_create_user(
    fake_logging_data,
    uwo,
):
    name: str = "test"
    telegram: int = 123
    result = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=name, telegram=telegram
    )
    user_id: int = result.data
    assert isinstance(user_id, int)


@pytest.mark.integration
@pytest.mark.asyncio
async def test_consistency_get_or_create_user(
    fake_logging_data,
    uwo,
):
    name: str = "test"
    telegram: int = 123
    result_1 = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=name, telegram=telegram
    )
    result_2 = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=name, telegram=telegram
    )
    user_id_1: int = result_1.data
    user_id_2: int = result_2.data
    assert user_id_1 == user_id_2


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_telegram_get_or_create_user(
    fake_logging_data,
    uwo,
):
    name: str = "test"
    telegram: str = "ERROR_CODE"
    result = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=name, telegram=telegram
    )
    assert ErorrCode.INVALID_TELEGRAM.name == result.error.code


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_user_name_get_or_create_user(
    fake_logging_data,
    uwo,
):
    name: str = 123
    telegram: str = 123
    result = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=name, telegram=telegram
    )
    assert ErorrCode.INVALID_USER_NAME.name == result.error.code
