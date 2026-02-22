from typing import List
from domain.repositories.executor import ExecutorRepository
from domain.repositories.genre import GenreRepository


class CreateUserExecutor:
    def __init__(
        self,
        executor_repo: ExecutorRepository,
        genre_repo: GenreRepository,
    ):
        self.executor_repo: ExecutorRepository = executor_repo
        self.genre_repo: GenreRepository = genre_repo

    async def execute(
        self,
        user_id: int,
        name: str,
        country: str,
        photo_file_id: str,
        photo_file_unique_id: str,
        genre_titles: List,
    ):

        # создаем жанры для исполнителя
        genres = await self.genre_repo.get_or_create_genres(
            titles=genre_titles,
        )

        # Создаем  исполнителя
        executor = await self.executor_repo.create_user_executor(
            user_id=user_id,
            name=name,
            country=country,
            photo_file_id=photo_file_id,
            photo_file_unique_id=photo_file_unique_id,
            genres=genres,
        )
