from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.db.models.sqlaclhemy.collection_song import CollectionSong


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
            )
        )
        collection_songs = stmt.all()
        return collection_songs
