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
