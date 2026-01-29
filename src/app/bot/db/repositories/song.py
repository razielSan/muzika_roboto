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
        order=1,
    ):
        list_songs = []
        for index, song in enumerate(song_repsonse, start=order):
            list_songs.append(
                self.model(
                    title=song.title,
                    file_id=song.file_id,
                    order=index,
                    album=album,
                )
            )

        self.session.add_all(list_songs)
        await self.sesiion.flush()
        return list_songs

    async def get_all_songs(self, album_id: int):
        stmt = await self.session.scalars(
            select(self.model).where(self.model.album_id == album_id)
        )
        songs = stmt.all()
        return songs

    async def get_song_by_order(self, album_id: int, order: int):
        song = await self.session.scalar(
            select(self.model).where(
                self.model.album_id == album_id,
                self.model.order == order,
            ),
        )
        return song

    async def delete_songs_by_orders(self, album_id: int, list_order: List[int]):

        await self.session.execute(
            delete(self.model).where(
                self.model.album_id == album_id,
                self.model.order.in_(list_order),
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
