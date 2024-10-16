import asyncio

from db import ENGINE, BASE


async def create_tables():
    async with ENGINE.begin() as conn:
        await conn.run_sync(BASE.metadata.drop_all)
        await conn.run_sync(BASE.metadata.create_all)

asyncio.run(create_tables())