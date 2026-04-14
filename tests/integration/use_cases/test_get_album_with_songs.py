import pytest

from application.use_cases.db.music_library.create_executor import CreateExecutor
from application.use_cases.db.music_library.add_album import AddAlbumExecutor
from application.use_cases.db.user.get_or_create_user import GetOrCreateUser
from application.use_cases.db.music_library.get.get_album_with_songs import (
    GetAlbumWithSongs,
)
from domain.errors.error_code import ErorrCode, SuccessCode, NotFoundCode
from domain.entities.response import SongResponse


@pytest.mark.integration
@pytest.mark.asyncio
async def test_succes(uwo, fake_logging_data):
    user_name: str = "user_name"
    telegram: int = 123

    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=user_name, telegram=telegram
    )
    user_id: int = user.data

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

    result = await GetAlbumWithSongs(uow=uwo, logging_data=fake_logging_data).execute(
        user_id=user_id, executor_id=executor_id, album_id=album_id
    )

    assert result.code == SuccessCode.GET_ALBUMS_SUCCESS.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_not_found(uwo, fake_logging_data):
    user_name: str = "user_name"
    telegram: int = 123

    name_executor: str = "executor"
    country: str = "country"
    photo_file_id: str = "executor_file_id"
    photo_file_unique_id: str = "executor_file_unique_id"
    genres = ["genres"]

    user = await GetOrCreateUser(uow=uwo, logging_data=fake_logging_data).execute(
        name=user_name, telegram=telegram
    )
    user_id: int = user.data

    executor = await CreateExecutor(uow=uwo, logging_data=fake_logging_data).execute(
        name=name_executor,
        country=country,
        user_id=user_id,
        photo_file_id=photo_file_id,
        photo_file_unique_id=photo_file_unique_id,
        genres_executor=genres,
    )
    executor_id = executor.data
    album_id = 1

    result = await GetAlbumWithSongs(uow=uwo, logging_data=fake_logging_data).execute(
        user_id=user_id, executor_id=executor_id, album_id=album_id
    )

    assert result.code == NotFoundCode.ALBUM_NOT_FOUND.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_user_id(uwo, fake_logging_data):
    user_id = "user_id"
    executor_id = 123
    album_id = 123

    result = await GetAlbumWithSongs(uow=uwo, logging_data=fake_logging_data).execute(
        user_id=user_id, executor_id=executor_id, album_id=album_id
    )

    assert result.error.code == ErorrCode.INVALID_USER_ID.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_executor_id(uwo, fake_logging_data):
    user_id = 123
    executor_id = "executor_id"
    album_id = 123

    result = await GetAlbumWithSongs(uow=uwo, logging_data=fake_logging_data).execute(
        user_id=user_id, executor_id=executor_id, album_id=album_id
    )

    assert result.error.code == ErorrCode.INVALID_EXECUTOR_ID.name


@pytest.mark.integration
@pytest.mark.asyncio
async def test_invalide_album_id(uwo, fake_logging_data):
    user_id = 123
    executor_id = 123
    album_id = "album_id"

    result = await GetAlbumWithSongs(uow=uwo, logging_data=fake_logging_data).execute(
        user_id=user_id, executor_id=executor_id, album_id=album_id
    )

    assert result.error.code == ErorrCode.INVALID_ALBUM_ID.name
