from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from infrastructure.db.models.sqlaclhemy.collection_songs import CollectionSongs
from domain.entities.response import CollectionSongsResponse
from domain.entities.db.repositories.collection_songs import CollectionSongsRepository


class SQLAlchemyCollectionSongsRepository(CollectionSongsRepository):
    model = CollectionSongs

    def __init__(self, session: AsyncSession):
        self.session: AsyncSession = session

    async def get_song(self, user_id: int, song_id: int) -> Optional[CollectionSongs]:
        song = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.id == song_id
            )
        )
        await self.session.flush()
        return song

    async def get_all_songs(
        self,
        user_id: int,
    ):
        stmt = await self.session.scalars(
            select(self.model)
            .where(
                self.model.user_id == user_id,
            )
            .order_by(self.model.position)
        )
        collection_songs = stmt.all()
        return collection_songs

    async def get_last_poistion_song(self, user_id: int) -> Optional[int]:
        stmt = await self.session.scalars(
            select(func.max(self.model.position)).where(
                self.model.user_id == user_id,
            )
        )
        max_position: Optional[int] = stmt.first()

        return max_position

    async def add_songs(
        self,
        collection_songs: List[CollectionSongsResponse],
        user_id: int,
        start_position: int = 1,
    ) -> List[CollectionSongs]:
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

    async def update_song_title(
        self,
        user_id: int,
        title: str,
        position: int,
    ) -> Optional[CollectionSongs]:
        song = await self.session.scalar(
            select(self.model).where(
                self.model.user_id == user_id, self.model.position == position
            )
        )
        if not song:
            return None

        song.title = title
        await self.session.flush()
        return song

    async def delete_songs(self, user_id: int, list_ids: List[int]) -> True:

        await self.session.execute(
            delete(self.model).where(
                self.model.user_id == user_id,
                self.model.id.in_(list_ids),
            )
        )
        await self.session.flush()
        return True
