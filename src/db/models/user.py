from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String

from ..base import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(Integer)
    utc_offset_minutes: Mapped[Optional[int]] = mapped_column(Integer)