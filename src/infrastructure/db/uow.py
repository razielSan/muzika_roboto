from sqlalchemy.ext.asyncio import AsyncSession


from domain.entities.db.uow import AbstractUnitOfWork
from infrastructure.db.db_helper import db_helper
from infrastructure.db.repositories.sqlaclhemy.executor import (
    SQLAlchemyExecutorRepository,
)
from infrastructure.db.repositories.sqlaclhemy.genre import SQLAlchemyGenreRepository
from infrastructure.db.repositories.sqlaclhemy.user import SQLAlchemyUserRepository
from infrastructure.db.repositories.sqlaclhemy.collection_songs import (
    SQLAlchemyCollectionSongsRepository,
)
from infrastructure.db.repositories.sqlaclhemy.album import SQLAlchemyAlbumRepository


class UnitOfWork(AbstractUnitOfWork):
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session: AsyncSession = db_helper.session()
        self.executors = SQLAlchemyExecutorRepository(session=self.session)
        self.genres = SQLAlchemyGenreRepository(session=self.session)
        self.users = SQLAlchemyUserRepository(session=self.session)
        self.collection_songs = SQLAlchemyCollectionSongsRepository(
            session=self.session
        )
        self.albums: SQLAlchemyAlbumRepository = SQLAlchemyAlbumRepository(
            session=self.session
        )
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()
