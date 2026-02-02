from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import CheckConstraint

from app.bot.models.base import Base


class Song(Base):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    position: Mapped[int] = mapped_column(
        CheckConstraint(
            "position > 0",
            name="position_positive",
        )
    )
    file_id: Mapped[str]
    file_unique_id: Mapped[str]

    album_id: Mapped[int] = mapped_column(ForeignKey("album.id", ondelete="CASCADE"))
    album: Mapped["Album"] = relationship(back_populates="songs")

    __table_args__ = (UniqueConstraint("album_id", "position"),)
