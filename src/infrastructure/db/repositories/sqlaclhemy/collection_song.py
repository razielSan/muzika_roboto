from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from infrastructure.db.models.sqlaclhemy.collection_song import CollectionSong
from domain.entities.response import CollectionSongResponse


class SQLAlchemyCollectionSongRepository:
    model = CollectionSong

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_all_songs(
        self,
        user_id: int,
    ):
        stmt = await self.session.scalars(
            select(self.model).where(
                self.model.user_id == user_id,
            ).order_by(self.model.position)
        )
        collection_songs = stmt.all()
        return collection_songs

    async def get_last_poistion_song(self, user_id: int):
        stmt = await self.session.scalars(
            select(func.max(self.model.position)).where(
                self.model.user_id == user_id,
            )
        )
        max_position = stmt.first()

        return max_position

    async def add_songs(
        self,
        collection_songs: List[CollectionSongResponse],
        user_id: int,
        start_position: int = 1,
    ):
        list_songs = []
        for position, song in enumerate(collection_songs, start=start_position):
            list_songs.append(
                self.model(
                    title=song.title,
                    file_id=song.file_id,
                    position=position,
                    user_id=user_id,
                    file_unique_id=song.file_unique_id,
                )
            )
        self.session.add_all(list_songs)
        await self.session.flush()
        return list_songs
