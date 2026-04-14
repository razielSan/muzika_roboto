import pytest

from application.use_cases.db.music_library.create_executor import CreateExecutor
from application.use_cases.db.user.get_or_create_user import GetOrCreateUser
from domain.errors.error_code import ErorrCode, SuccessCode


@pytest.mark.integration
@pytest.mark.asyncio
async def test_success_create_executor(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name: str = "test"
    country: str = "test"
    genres = ["test"]
    photo_file_id: str = "test"
    photo_file_umique_id: str = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.code == SuccessCode.ADD_EXECUTOR_SUCCESS.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_executor_already_exists(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name: str = "test"
    country: str = "test"
    genres = ["test"]
    photo_file_id: str = "test"
    photo_file_umique_id: str = "test"

    await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )

    executor_name_2: str = "TEST"
    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name_2,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.EXECUTOR_ALREADY_EXISTS.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_executor_name(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = 123
    country = "test"
    genres = ["test"]
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_EXECUTOR_NAME.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_empty_executor_name(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = ""
    country = "test"
    genres = ["test"]
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_LEN_DATA.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_executor_country(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = "test"
    country = 123
    genres = ["test"]
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_EXECUTOR_COUNTRY.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_empty_executor_country(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = "test"
    country = "   "
    genres = ["test"]
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_LEN_DATA.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_executor_genres(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = "test"
    country = "test"
    genres = 123
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_EXECUTOR_GENRES.name
    
    
@pytest.mark.integration
@pytest.mark.asyncio
async def test_empty_executor_genres(
    fake_logging_data,
    uwo,
):
    user_name: str = "test"
    telegram: int = 123

    user_result = await GetOrCreateUser(
        uow=uwo, logging_data=fake_logging_data
    ).execute(
        name=user_name,
        telegram=telegram,
    )

    user_id: int = user_result.data

    executor_name = "test"
    country = "test"
    genres = []
    photo_file_id = "test"
    photo_file_umique_id = "test"

    result = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=executor_name,
        country=country,
        genres_executor=genres,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_umique_id,
    )
    assert result.error.code == ErorrCode.INVALID_LEN_DATA.name

