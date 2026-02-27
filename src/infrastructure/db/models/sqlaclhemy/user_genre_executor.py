from __future__ import annotations
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, BigInteger

from infrastructure.db.models.sqlaclhemy.base import Base


class User(Base):

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    telegram: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        nullable=False,
        index=True,
    )

    collection_song_photo_file_id: Mapped[Optional[str]] = mapped_column(nullable=True)
    collection_song_photo_unique_id: Mapped[Optional[str]] = mapped_column(
        nullable=True
    )

    # свои собственные исполнители
    executors: Mapped[List["Executor"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )

    # Добавленные из общей библиотеки
    library_executors: Mapped[List["Executor"]] = relationship(
        secondary="user_executor", back_populates="library_users"
    )

    collection_songs: Mapped[List["CollectionSong"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )


class UserExecutor(Base):
    __tablename__ = "user_executor"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        primary_key=True,
    )
    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executor.id", ondelete="CASCADE"),
        primary_key=True,
    )


class GenreExecutor(Base):
    __tablename__ = "genre_executor"

    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executor.id", ondelete="CASCADE"), primary_key=True
    )
    genre_id: Mapped[int] = mapped_column(
        ForeignKey("genre.id", ondelete="CASCADE"),
        primary_key=True,
    )


class Executor(Base):
    __tablename__ = "executor"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    country: Mapped[str]

    photo_file_id: Mapped[str]
    photo_file_unique_id: Mapped[str]

    albums: Mapped[List["Album"]] = relationship(
        back_populates="executor",
        cascade="all, delete-orphan",
    )

    genres: Mapped[List[Genre]] = relationship(
        back_populates="executors",
        secondary="genre_executor",
    )
    library_users: Mapped[List["User"]] = relationship(
        secondary="user_executor", back_populates="library_executors"
    )

    # NULL → глобальный
    # NOT NULL → пользовательский
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"),
        nullable=True,
    )
    user: Mapped[Optional["User"]] = relationship(back_populates="executors")

    __table_args__ = (
        UniqueConstraint(
            "name",
            "country",
            name="name_country_uc",
        ),
    )

    def __repr__(self) -> str:
        return str(self.name)


class Genre(Base):
    __tablename__ = "genre"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(unique=True)

    executors: Mapped[List[Executor]] = relationship(
        back_populates="genres",
        secondary="genre_executor",
    )

    def __repr__(self) -> str:
        return str(self.title)
