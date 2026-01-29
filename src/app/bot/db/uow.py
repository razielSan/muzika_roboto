from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.db.db_helper import db_helper
from app.bot.db.repositories.user import UserSqlalchemyRepository
from app.bot.db.repositories.executor import ExecutorSqlalchemyRepository
from app.bot.db.repositories.genre import GenreSqlalchemyRepository
from app.bot.db.repositories.album import AlbumSQLAlchemyRepository
from app.bot.db.repositories.song import SongSQLAlchemyRepository


class UnitOfWork:
    def __init__(self):
        self.session = None

    async def __aenter__(self):
        self.session: AsyncSession = db_helper.session()
        self.users = UserSqlalchemyRepository(session=self.session)
        self.genres = GenreSqlalchemyRepository(session=self.session)
        self.executors = ExecutorSqlalchemyRepository(session=self.session)
        self.albums = AlbumSQLAlchemyRepository(session=self.session)
        self.songs = SongSQLAlchemyRepository(session=self.session)
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc:
            await self.session.rollback()
        else:
            await self.session.commit()

        await self.session.close()


# class UnitOfWork:
#     def __init__(self):
#         self.session: AsyncSession | None = None

#     async def __aenter__(self):
#         self.session = db_helper.session()
#         self.users = UserSqlalchemyRepository(self.session)
#         return self

#     async def __aexit__(self, exc_type, exc, tb):
#         if exc:
#             await self.session.rollback()
#         else:
#             await self.session.commit()

#         await self.session.close()
