import pytest

from app.bot.modules.music_library.childes.executor.use_cases.update import (
    process_update_album_year,
)
from infrastructure.aiogram.fsm.data import UpdateAlbumYearData
from application.use_cases.db.user.get_or_create_user import GetOrCreateUser
from application.use_cases.db.music_library.create_executor import CreateExecutor
from application.use_cases.db.music_library.add_album import AddAlbumExecutor
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.response import SongResponse


@pytest.mark.integration
@pytest.mark.asyncio
async def test_succes(uwo, fake_logging_data):

    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user_id = None

    executor = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=name_executor,
        country=country,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
        genres_executor=genres,
    )
    executor_id = executor.data
    title = "title"
    year = 123
    album_photo_file_id: str = "album_file_id"
    album_photo_file_unique_id: str = "album_file_unique_id"
    songs = [
        SongResponse(
            title="song",
            file_id="song_file_id",
            file_unique_id="song_file_unique_id",
        )
    ]
    album = await AddAlbumExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        executor_id=executor_id,
        title=title,
        year=year,
        photo_file_id=album_photo_file_id,
        photo_file_unique_id=album_photo_file_unique_id,
        songs=songs,
    )
    album_id = album.data

    state_data = UpdateAlbumYearData(
        current_page_executor=1,
        music_library_album=True,
        executor_id=executor_id,
        user_id=user_id,
        album_id=album_id,
        is_global_executor=True,
        album_position=0,
        is_admin=True,
        year=None,
    )

    year = "123"
    result = await process_update_album_year(
        logging_data=fake_logging_data, uwo=uwo, number=year, state_data=state_data
    )

    assert result.code == SuccessCode.UPDATE_ALBUM_YEAR_SUCCESS.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_not_found_album(uwo, fake_logging_data):

    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user_id = None

    executor = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=name_executor,
        country=country,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
        genres_executor=genres,
    )

    state_data = UpdateAlbumYearData(
        current_page_executor=1,
        music_library_album=True,
        executor_id=executor.data,
        user_id=user_id,
        album_id=1,
        is_global_executor=True,
        album_position=0,
        is_admin=True,
        year=None,
    )

    year = "123"
    result = await process_update_album_year(
        logging_data=fake_logging_data, uwo=uwo, number=year, state_data=state_data
    )

    assert result.code == NotFoundCode.ALBUM_NOT_FOUND.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalid_year(uwo, fake_logging_data):
    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user_id = None

    executor = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=name_executor,
        country=country,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
        genres_executor=genres,
    )
    executor_id = executor.data
    title = "title"
    year = 123
    album_photo_file_id: str = "album_file_id"
    album_photo_file_unique_id: str = "album_file_unique_id"
    songs = [
        SongResponse(
            title="song",
            file_id="song_file_id",
            file_unique_id="song_file_unique_id",
        )
    ]
    album = await AddAlbumExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        executor_id=executor_id,
        title=title,
        year=year,
        photo_file_id=album_photo_file_id,
        photo_file_unique_id=album_photo_file_unique_id,
        songs=songs,
    )
    album_id = album.data

    state_data = UpdateAlbumYearData(
        current_page_executor=1,
        music_library_album=True,
        executor_id=executor_id,
        user_id=user_id,
        album_id=album_id,
        is_global_executor=True,
        album_position=0,
        is_admin=True,
        year=None,
    )

    year = "year"
    result = await process_update_album_year(
        logging_data=fake_logging_data, uwo=uwo, number=year, state_data=state_data
    )

    assert result.error.code == ErorrCode.FAILED_CHECK_POSITIVITY.name
