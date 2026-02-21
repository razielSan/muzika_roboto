from typing import List, Set

from sqlalchemy.ext.asyncio import AsyncSession

from infrastructure.db.models.sqlaclhemy import Song
from app.bot.view_model import SongResponse
from sqlalchemy import select, delete, func


class SongSQLAlchemyRepository:
    model = Song

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_songs(
        self,
        song_repsonse: List[SongResponse],
        album_id: int,
        start_position: int = 1,
    ):
        list_songs = []
        for position, song in enumerate(song_repsonse, start=start_position):
            list_songs.append(
                self.model(
                    title=song.title,
                    file_id=song.file_id,
                    position=position,
                    album_id=album_id,
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

    async def get_last_poistion_song(self, album_id: int):
        stmt = await self.session.scalars(
            select(func.max(self.model.position)).where(self.model.album_id == album_id)
        )
        max_position = stmt.first()

        return max_position

    async def update_title_song(
        self,
        album_id: int,
        title: str,
        position: int,
    ):
        song = await self.session.scalar(
            select(self.model).where(
                self.model.album_id == album_id,
                self.model.position == position,
            ),
        )

        if not song:
            return False
        song.title = title
        await self.session.flush()
        return song

    async def delete_songs(self, album_id: int, list_ids: List[int]):

        await self.session.execute(
            delete(self.model).where(
                self.model.album_id == album_id,
                self.model.id.in_(list_ids),
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

    async def get_positions_songs_by_id(
        self,
        album_id: int,
        songs_ids: List,
    ):
        stmt = await self.session.scalars(
            select(self.model).where(
                self.model.album_id == album_id, self.model.id.in_(songs_ids)
            )
        )
        songs = stmt.all()
        songs_position = [song.position for song in songs]
        return songs_position
