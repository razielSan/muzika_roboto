from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.bot.models import Song, Album
from app.bot.db.response import SongResponse
from sqlalchemy import select, delete


class SongSQLAlchemyRepository:
    model = Song

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_songs(
        self,
        song_repsonse: List[SongResponse],
        album: Album,
    ):
        list_songs = []
        for song in song_repsonse:
            list_songs.append(
                self.model(
                    title=song.title,
                    file_id=song.file_id,
                    position=song.position,
                    album=album,
                    file_unique_id=song.file_unique_id,
                )
            )
        self.session.add_all(list_songs)
        await self.session.flush()
        return list_songs

    async def get_all_songs(self, album_id: int):
        stmt = await self.session.scalars(
            select(self.model).where(self.model.album_id == album_id)
        )
        songs = stmt.all()
        return songs

    async def get_song_by_position(self, album_id: int, position: int):
        song = await self.session.scalar(
            select(self.model).where(
                self.model.album_id == album_id,
                self.model.position == position,
            ),
        )
        return song

    async def delete_songs_by_orders(self, album_id: int, list_postions: List[int]):

        await self.session.execute(
            delete(self.model).where(
                self.model.album_id == album_id,
                self.model.position.in_(list_postions),
            )
        )
        await self.session.flush()
        return True

    async def delete_all_songs(self, album_id: int):
        await self.session.execute(
            delete(self.model).where(self.model.album_id == album_id)
        )
        await self.session.flush()
        return True
