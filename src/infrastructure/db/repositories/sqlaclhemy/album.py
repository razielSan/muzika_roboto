from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from domain.entities.db.repositories.album import AlbumRepository
from infrastructure.db.models.sqlaclhemy import Album


class SQLAlchemyAlbumRepository(AlbumRepository):
    model: Album = Album

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def create_album(
        self,
        executor_id: int,
        title: str,
        year: int,
        photo_file_id: str,
        photo_file_unique_id: str,
    ) -> Album:
        album = self.model(
            executor_id=executor_id,
            title=title,
            year=year,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
        )
        self.session.add(album)
        await self.session.flush()
        return album

    async def get_album_by_title(
        self,
        executor_id: int,
        title: str,
    ) -> Optional[Album]:
        album: Optional[Album] = await self.session.scalar(
            select(self.model)
            .where(
                self.model.executor_id == executor_id,
                self.model.title == title,
            )
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

    async def get_album(
        self,
        executor_id: int,
        album_id: int,
    ) -> Optional[Album]:
        album: Optional[Album] = await self.session.scalar(
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

    async def delete_album(self, executor_id: int, album_id: int) -> bool:
        album = await self.session.scalar(
            select(self.model).where(
                self.model.id == album_id, self.model.executor_id == executor_id
            )
        )
        if not album:
            return False

        await self.session.delete(album)
        await self.session.flush()
        return True
