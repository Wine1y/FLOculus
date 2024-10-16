from typing import Optional, List, TypeVar, Generic, Any, Callable, AsyncGenerator

from sqlalchemy import select, func, Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError

from .base import async_session, BaseModel


model = TypeVar("model", bound=BaseModel)
class Repository(Generic[model]):
    session: AsyncSession
    repository_model: model

    def __init__(self):
        self.session = async_session()

    async def close(self) -> None:
        await self.session.close()

    async def __aenter__(self) -> "Repository[model]":
        return self
    
    async def __aexit__(self, type_: Any, value: Any, traceback: Any) -> None:
        await self.close()

    async def create(self, obj: model) -> bool:
        try:
            self.session.add(obj)
            await self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False
    
    async def create_all(self, objs: List[model]) -> bool:
        try:
            self.session.add_all(objs)
            await self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False
    
    async def get(self, id: int) -> Optional[model]:
        try:
            return await self.session.get(self.repository_model, id)
        except (IntegrityError, ProgrammingError, OperationalError):
            return None
    
    async def commit(self) -> bool:
        try:
            await self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False

    async def delete(self, obj: model) -> bool:
        try:
            await self.session.delete(obj)
            await self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False
    
    async def count(self) -> int:
        try:
            query = select(func.count()).select_from(self.repository_model)
            return (await self.session.execute(query)).scalar()
        except (IntegrityError, ProgrammingError, OperationalError):
            return 0

    async def get_first(
        self,
        filter_func: Callable[[Select], Select] | None = None
    ) -> Optional[model]:
        query = select(self.repository_model)
        if filter_func is not None:
            query = filter_func(query)
        res = (await self.session.execute(query)).first()
        return res[0] if res else None
        
    async def get_all(
        self,
        offset: int | None = 0,
        limit: int | None = 30,
        filter_func: Callable[[Select], Select] | None = None,
        sorting_func: Callable[[Select], Select] | None = None,
    ) -> List[model]:
        query = select(self.repository_model).offset(offset).limit(limit)
        if filter_func is not None:
            query = filter_func(query)
        query = sorting_func(query) if sorting_func is not None else query.order_by(self.repository_model.id)
        res = (await self.session.execute(query)).all()
        return [row[0] for row in res]