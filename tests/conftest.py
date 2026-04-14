import logging

import pytest_asyncio
import pytest

from infrastructure.db.models.sqlaclhemy import Base
from tests.db_helper import TestSession, test_engine
from infrastructure.db.uow import UnitOfWork
from core.response.response_data import LoggingData


@pytest_asyncio.fixture(
    scope="session",
    autouse=True,
    loop_scope="session",
)
async def setup_db():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture
def fake_logging_data():
    logger = logging.getLogger("test")
    logger.addHandler(logging.NullHandler())

    return LoggingData(
        router_name="test",
        error_logger=logger,
        warning_logger=logger,
        info_logger=logger,
        critical_logger=logger,
    )


@pytest_asyncio.fixture
async def uwo():
    return UnitOfWork(session_factory=TestSession)


@pytest_asyncio.fixture(autouse=True)
async def clean_db():
    yield
    async with test_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            await conn.execute(table.delete())
