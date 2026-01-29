from app.bot.models import Album, Executor

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload


class AlbumSQLAlchemyRepository:
    model = Album

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_album(
        self,
        executor: Executor,
        title: str,
        year: int,
    ):
        album = self.model(
            executor=executor,
            title=title,
            year=year,
        )
        self.session.add(album)
        await self.session.flush()
        return album

    async def get_album(self, executor_id: int, album_id: int):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id, self.model.id == album_id
            )
        )
        return album

    async def get_all_albums(self, executor_id: int):
        stmt = await self.session.scalars(
            select(self.model)
            .where(
                self.model.executor_id == executor_id,
            )
            .options(
                selectinload(
                    self.model.executor,
                )
            )
            .options(
                selectinload(
                    self.model.songs,
                ),
            ),
        )

        albums = stmt.all()
        return albums

    async def update_title(self, executor_id: int, title: str, album_id: int):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id, self.model.id == album_id
            )
        )
        album.title = title
        self.session.add(album)
        await self.session.flush()
        return album

    async def update_year(self, executor_id: int, year: int, album_id: int):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id, self.model.id == album_id
            )
        )
        album.year = year
        self.session.add(album)
        await self.session.flush()
        return album

    async def delete_album(self, executor_id: int, album_id: int):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id, self.model.id == album_id
            )
        )
        if not album:
            return False

        await self.session.delete(album)
        await self.session.flush()
        return True
