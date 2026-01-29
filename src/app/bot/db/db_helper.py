from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.bot.settings import settings


class DataBaseHelper:
    def __init__(self, url: str = settings.ASYNC_SQLITE_BASE):
        self.async_engine = create_async_engine(url=url, echo=False)
        self.session_factory = async_sessionmaker(bind=self.async_engine)

    def session(self) -> AsyncSession:
        return self.session_factory()


db_helper = DataBaseHelper()
