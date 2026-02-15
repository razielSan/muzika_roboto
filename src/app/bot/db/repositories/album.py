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
        photo_file_unique_id: str,
        photo_file_id: str,
    ):
        album = self.model(
            executor=executor,
            title=title,
            year=year,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
        )
        self.session.add(album)
        await self.session.flush()
        return album

    async def get_album(self, executor_id: int, album_id: int):
        album = await self.session.scalar(
            select(self.model)
            .where(self.model.executor_id == executor_id, self.model.id == album_id)
            .options(
                selectinload(
                    self.model.songs,
                )
            )
            .options(
                selectinload(
                    self.model.executor,
                )
            ),
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

    async def get_album_by_title(
        self,
        executor_id: int,
        title: str,
    ):
        album = await self.session.scalar(
            select(self.model)
            .where(
                self.model.executor_id == executor_id,
                self.model.title == title,
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

        return album

    async def update_title(self, executor_id: int, title: str, album_id: int):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id,
                self.model.id == album_id,
            )
        )
        album.title = title
        await self.session.flush()
        return album

    async def update_year(
        self,
        executor_id: int,
        year: int,
        album_id: int,
    ):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.executor_id == executor_id, self.model.id == album_id
            )
        )
        album.year = year
        await self.session.flush()
        return album

    async def update_photo_file_id_and_photo_file_unique_id(
        self,
        executor_id: int,
        album_id: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ):
        album = await self.session.scalar(
            select(self.model).where(
                self.model.id == album_id,
                self.model.executor_id == executor_id,
            )
        )
        album.photo_file_id = photo_file_id
        album.photo_file_unique_id = photo_file_unique_id
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
