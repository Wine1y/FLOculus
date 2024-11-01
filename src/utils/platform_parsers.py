from classes.parsers import FlRuParser, FreelanceRuParser, HabrParser, KworkParser
from db import Platform, PlatformRepository


PLATFORM_TO_PARSER = {
    "fl.ru": FlRuParser,
    "freelance.ru": FreelanceRuParser,
    "freelance.habr.com": HabrParser,
    "kwork.ru": KworkParser
}

async def init_platforms_db():
    async with PlatformRepository() as rep:
        existing_platform_keys = {platform.name for platform in await rep.get_all(limit=None)}
        new_platforms = [
            Platform(name=platform_key)
            for platform_key in PLATFORM_TO_PARSER
            if platform_key not in existing_platform_keys
        ]
        await rep.create_all(new_platforms)
        