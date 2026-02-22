from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from infrastructure.db.settings import data_base_settings

print(data_base_settings.DATABASE_DIR)


class DataBaseHelper:
    def __init__(self, url: str = data_base_settings.ASYNC_SQLITE_BASE):
        self.async_engine = create_async_engine(url=url, echo=False)
        self.session_factory = async_sessionmaker(bind=self.async_engine)

    def session(self) -> AsyncSession:
        return self.session_factory()


db_helper = DataBaseHelper()
