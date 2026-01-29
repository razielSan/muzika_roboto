from typing import List

from app.bot.models.base import Base

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import BigInteger


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

    executors: Mapped[List["Executor"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
    )
