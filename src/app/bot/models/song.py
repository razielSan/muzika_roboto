from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy import CheckConstraint

from app.bot.models.base import Base


class Song(Base):
    __tablename__ = "song"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    order: Mapped[int] = mapped_column(
        CheckConstraint(
            "order > 0",
            name="order_positive",
        )
    )
    file_id: Mapped[str] = mapped_column(index=True, unique=True)

    album_id: Mapped[int] = mapped_column(
        ForeignKey("album.id", ondelete="CASCADE")
    )
    album: Mapped["Album"] = relationship(back_populates="songs")

    __table_args__ = (UniqueConstraint("title", "album_id", "order"),)
