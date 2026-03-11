from abc import ABC, abstractmethod

from domain.entities.db.repositories.executor import ExecutorRepository
from domain.entities.db.repositories.collection_songs import CollectionSongsRepository
from domain.entities.db.repositories.genre import GenreRepository
from domain.entities.db.repositories.user import UserRepository
from domain.entities.db.repositories.song import SongRepository
from domain.entities.db.repositories.user_executor import UserExecutorRepository


class AbstractUnitOfWork(ABC):
    executors: ExecutorRepository
    users: UserRepository
    genres: GenreRepository
    collection_songs: CollectionSongsRepository
    songs: SongRepository
    user_executors: UserExecutorRepository

    async def __aenter__(self):
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc, tb):
        pass
