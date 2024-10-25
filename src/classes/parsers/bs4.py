from abc import ABC

from aiohttp import ClientSession
from bs4 import BeautifulSoup, Tag

from .base import PlatformParser


class BS4PlatformParser(PlatformParser, ABC):
    session: ClientSession
    request_delay_seconds: float = 1.25
    base_url: str

    async def __aenter__(self):
        self.session = ClientSession()
        return self
    
    async def __aexit__(self, *_excinfo):
        await self.session.close()
    
    async def _get_page_soup(self, path: str) -> BeautifulSoup:
        resp = await self.session.get(f"{self.base_url}{path}")
        return BeautifulSoup(await resp.text(), features="lxml")
    
    def _get_tag_text(self, tag: Tag | None, separator: str='\n') -> str | None:
        if tag is None:
            return None
        return tag.get_text(separator, strip=True).replace('\xa0', ' ').strip("\r\n\t ")