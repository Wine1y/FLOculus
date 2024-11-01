from typing import Optional

from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy import Integer, String

from ..base import BaseModel


class Platform(BaseModel):
    __tablename__ = "platforms"

    name: Mapped[str] = mapped_column(String(32), unique=True)
    last_time_mark: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)