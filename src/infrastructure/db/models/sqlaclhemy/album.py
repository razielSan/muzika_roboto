from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint, Index

from infrastructure.db.models.sqlaclhemy.base import Base


class Album(Base):

    __tablename__ = "album"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    year: Mapped[int]

    executor_id: Mapped[int] = mapped_column(
        ForeignKey("executor.id", ondelete="CASCADE")
    )

    photo_file_id: Mapped[str]
    photo_file_unique_id: Mapped[str]

    executor: Mapped["Executor"] = relationship(back_populates="albums")
    songs: Mapped[List["Song"]] = relationship(
        back_populates="album",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint(
            "title",
            "executor_id",
            name="executorname_title_executorid_uc",
        ),
        Index("idx_album_executor", "executor_id"),
    )
