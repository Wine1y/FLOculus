from typing import Optional, List

from sqlalchemy.orm import mapped_column, Mapped, relationship
from sqlalchemy import Integer

from ..base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer)
    utc_offset_minutes: Mapped[Optional[int]] = mapped_column(Integer)
    filters: Mapped[List["FilterEntry"]] = relationship(back_populates="owner")