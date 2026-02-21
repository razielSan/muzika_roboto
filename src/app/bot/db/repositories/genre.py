from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from infrastructure.db.models.sqlaclhemy import Genre


class GenreSqlalchemyRepository:
    model = Genre

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_or_create_genres(self, titles: List[str]):
        result = await self.session.scalars(
            select(Genre).where(self.model.title.in_(titles)),
        )
        existing = {genre.title: genre for genre in result.all()}

        genres = []
        for title in titles:
            if title in existing:
                genres.append(existing[title])
            else:
                genre = self.model(
                    title=title,
                )
                self.session.add(genre)
                genres.append(genre)
        await self.session.flush()
        return genres
