from typing import Optional, List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer, Table, Column, ForeignKey

from ..base import BaseModel, BASE
from .platform import Platform


users_disabled_platforms = Table(
    "users_disabled_platforms",
    BASE.metadata,
    Column("user_id", ForeignKey("users.id"), primary_key=True),
    Column("platform_id", ForeignKey("platforms.id"), primary_key=True)
)


class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer)
    utc_offset_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    filters: Mapped[List["FilterEntry"]] = relationship(back_populates="owner")
    disabled_platforms: Mapped[List[Platform]] = relationship(secondary=users_disabled_platforms)