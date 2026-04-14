from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker


test_engine = create_async_engine(
    url="sqlite+aiosqlite:///:memory:",
    echo=False,
)

TestSession = async_sessionmaker(bind=test_engine)
