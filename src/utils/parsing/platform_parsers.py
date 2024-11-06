import logging
from typing import Dict, Type

from classes.parsers import PlatformParser, FlRuParser, FreelanceRuParser, HabrParser, KworkParser
from db import Platform, PlatformRepository


PLATFORM_TO_PARSER: Dict[str, Type[PlatformParser]] = {
    "fl.ru": FlRuParser,
    "freelance.ru": FreelanceRuParser,
    "freelance.habr.com": HabrParser,
    "kwork.ru": KworkParser
}

log = logging.getLogger(__name__)

async def init_platforms_db():
    log.debug("Initializing platforms in DB")
    async with PlatformRepository() as rep:
        existing_platform_keys = {platform.name for platform in await rep.get_all(limit=None)}
        new_platforms = [
            Platform(name=platform_key)
            for platform_key in PLATFORM_TO_PARSER
            if platform_key not in existing_platform_keys
        ]
        log.debug(f"Creating {len(new_platforms)} new platform entries in the database: {new_platforms}")
        await rep.create_all(new_platforms)
        