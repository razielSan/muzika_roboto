from typing import List

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey
from sqlalchemy import CheckConstraint, UniqueConstraint

from infrastructure.db.models.sqlaclhemy.base import Base


class CollectionSong(Base):
    __tablename__ = "collection_song"

    id: Mapped[int] = mapped_column(primary_key=True)

    title: Mapped[str]
    position: Mapped[int] = mapped_column(
        CheckConstraint(
            "position > 0",
            name="position_positive",
        )
    )
    collection_photo_file_id: Mapped[str]
    collection_photo_unique_id: Mapped[str]
    file_id: Mapped[str]
    file_unique_id: Mapped[str]

    user_id: Mapped[int] = mapped_column(ForeignKey("user.id", ondelete="CASCADE"))
    user: Mapped["User"] = relationship(back_populates="collection_songs")

    __table_args__ = (UniqueConstraint("user_id", "position"),)
