from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from domain.entities.db.repositories.song import SongRepository
from domain.entities.response import SongResponse
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

    async def get_last_postion_song(self, album_id: int) -> Optional[int]:
        position = await self.session.scalar(
            select(func.max(self.model.position)).where(self.model.album_id == album_id)
        )
        return position

    async def add_songs(
        self,
        songs: List[SongResponse],
        album_id: int,
        start_position: int = 1,
    ) -> List[Song]:
        songs_albums = []
        for position, song in enumerate(songs, start=start_position):
            songs_albums.append(
                self.model(
                    title=song.title,
                    position=position,
                    album_id=album_id,
                    file_id=song.file_id,
                    file_unique_id=song.file_unique_id,
                )
            )
        self.session.add_all(songs_albums)
        await self.session.flush()
        return songs

    async def update_title_song(
        self,
        position: int,
        album_id: int,
        title: str,
    ) -> Optional[Song]:
        song: Optional[Song] = await self.session.scalar(
            select(self.model).where(
                self.model.position == position,
                self.model.album_id == album_id,
            )
        )
        if not song:
            return None
        song.title = title
        await self.session.flush()
        return song

    async def delete_songs(
        self,
        album_id: int,
        songs_ids: List[int],
    ) -> True:
        await self.session.execute(
            delete(self.model).where(
                self.model.album_id == album_id, self.model.id.in_(songs_ids)
            )
        )

        await self.session.flush()
        return True
