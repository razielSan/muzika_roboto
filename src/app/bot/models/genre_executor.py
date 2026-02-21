from __future__ import annotations
from typing import List, Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from app.bot.models.base import Base


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
