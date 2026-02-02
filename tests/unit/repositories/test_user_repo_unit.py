import pytest

from app.bot.db.repositories.user import UserSqlalchemyRepository


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_get_user(async_session):
    repo = UserSqlalchemyRepository(session=async_session)

    name = "test"
    telegram = 123

    user = await repo.create_user(name=name, telegram=telegram)

    await async_session.commit()

    assert user.id is not None

    user = await repo.get_user_by_telegram(telegram=telegram)

    assert user.name == name
    assert user.telegram == telegram
