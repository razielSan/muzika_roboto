from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from infrastructure.db.settings import data_base_settings


class DataBaseHelper:
    def __init__(
        self,
    ):
        db_path = data_base_settings.DATABASE_DIR
        db_path.parent.mkdir(parents=True, exist_ok=True)

        self.async_engine = create_async_engine(
            url=data_base_settings.ASYNC_SQLITE_BASE, echo=False
        )
        self.session_factory = async_sessionmaker(bind=self.async_engine)

    def session(self) -> AsyncSession:
        return self.session_factory()


db_helper = DataBaseHelper()
