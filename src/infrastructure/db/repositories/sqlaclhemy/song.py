from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from domain.entities.db.repositories.song import SongRepository
from infrastructure.db.models.sqlaclhemy.song import Song



class SQLAlchemySongRepository(SongRepository):
    model = Song

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_song(self, album_id: int, song_id: int) -> Optional[Song]:
        song = await self.session.scalar(
            select(self.model).where(
                self.model.album_id == album_id, self.model.id == song_id
            )
        )
        await self.session.flush()
        return song
