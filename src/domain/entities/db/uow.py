from domain.entities.db.repositories.executor import ExecutorRepository
from domain.entities.db.repositories.genre import GenreRepository
from domain.entities.db.repositories.user import UserRepository


class UnitOfWork:
    executors: ExecutorRepository
    users: UserRepository
    genres: GenreRepository

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc, tb):
        pass
