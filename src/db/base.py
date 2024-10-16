from os import getenv
from datetime import datetime, timezone

from sqlalchemy import Integer, DateTime
from sqlalchemy.ext.asyncio import AsyncAttrs, create_async_engine, async_sessionmaker
from sqlalchemy.orm import mapped_column, declarative_base


DB_PATH = getenv("DATABASE_URL") or "sqlite+aiosqlite:///./db.sqlite"
ENGINE = create_async_engine(DB_PATH)
BASE = declarative_base()

async_session = async_sessionmaker(ENGINE, expire_on_commit=False)


class BaseModel(AsyncAttrs, BASE):
    __abstract__ = True

    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    created = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc))
    updated = mapped_column(DateTime, nullable=False, default=datetime.now(timezone.utc), onupdate=datetime.now(timezone.utc))

    def update(self, **fields):
        for name, value in fields.items():
            setattr(self, name, value)