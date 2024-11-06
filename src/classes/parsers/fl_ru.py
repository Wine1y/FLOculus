import asyncio
import re
from typing import AsyncGenerator
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

from bs4 import BeautifulSoup

from .bs4 import BS4PlatformParser
from ..tasks import FlRuTask, FlRuTaskAuthor, PriceType


PRICE_RE = re.compile(r"(?:(?:До (?P<max_price>[\d ]+))|(?:Более (?P<min_price>[\d ]+))|(?:(?P<price_range>[\d ]+ — [\d ]+))|(?:(?P<fixed_price>[\d ]+))) ?(?P<price_type>(?:₽/заказ)|(?:руб/заказ)|(?:₽/час)|₽)")
WRITE_RE = re.compile(r"document\.write\([\'\"](?P<html>.+)[\'\"]\);?")
PRICE_TYPES = {
    "₽/час": PriceType.PER_HOUR,
    "₽/заказ": PriceType.PER_PROJECT,
    "руб/заказ": PriceType.PER_PROJECT,
    "₽": PriceType.PER_PROJECT,
}

class FlRuParser(BS4PlatformParser):
    name: str = "fl.ru"
    base_url: str = "https://www.fl.ru"

    async def _parse_tasks(self) -> AsyncGenerator[FlRuTask, None]:
        page = 1
        path = "/projects/"
        while True:
            soup = await self._get_page_soup(path)
            await asyncio.sleep(self.request_delay_seconds)
            for div in soup.select("div#projects-list div.b-post__grid"):
                footer_html = WRITE_RE.match(
                    self._get_tag_text(div.select_one("div.b-post__foot script"))
                ).group("html")
                footer_soup = BeautifulSoup(footer_html, features="lxml")

                if self._get_tag_text(footer_soup.select_one("span.b-post__bold.text-7")).lower() != "заказ":
                    continue

                path = div.select_one(".b-post__title a").attrs.get("href")
                raised = div.select_one(".b-post__title.b-post__pin") is not None
                responses_str = self._get_tag_text(footer_soup.select_one("span[data-id=\"fl-view-count-href\"]"))
                if responses_str == "Исполнитель определён":
                    continue
                if responses_str == "Нет ответов":
                    responses = 0
                else:
                    responses = int(''.join(responses_str.split(' ')[:-1]))

                yield (await self._parse_task(path, responses, raised))
                await asyncio.sleep(self.request_delay_seconds)

            pager_html = WRITE_RE.match(
                self._get_tag_text(soup.select_one("div.b-pager .b-pager__back-next script"))
            ).group("html")
            pager_soup = BeautifulSoup(pager_html, features="lxml")
            if pager_soup.select_one("li.b-pager__next") is None:
                break
            page+=1
            path = f"/projects/category/programmirovanie/page-{page}/"
    
    async def _parse_task(self, path: str, responses: int=0, raised: bool=False) -> FlRuTask:
        soup = await self._get_page_soup(path)
        task_id = Path(path).parent.stem

        author = FlRuTaskAuthor(
            name=None,
            positive_reviews=abs(int(
                self._get_tag_text(soup.select_one("span.text-8.b-layout__txt_color_6db335")).replace(' ', '')
            )),
            negative_reviews=abs(int(
                self._get_tag_text(soup.select_one("span.text-8.b-layout__txt_color_c10600")).replace(' ', '')
            ))
        )

        price_str = self._get_tag_text(
            soup.select_one("div.text-right>div.text-4:first-child > span")
        ).replace('\n', '')
        price_match: re.Match = PRICE_RE.match(price_str)

        if price_match is None:
            price = min_price = max_price = None
            price_type = PriceType.UNDEFINED
        else:
            price_type=PRICE_TYPES.get(price_match.group("price_type")) or PriceType.UNDEFINED
            price = int(group.replace(' ', '')) if (group := price_match.group("fixed_price")) is not None else None
            min_price, max_price = price_match.group("min_price"), price_match.group("max_price")
            if (group := price_match.group("price_range")) is not None:
                min_price, max_price = group.replace(' ', '').split('—')
            min_price = int(min_price.replace(' ', '')) if min_price is not None else None
            max_price = int(max_price.replace(' ', '')) if max_price is not None else None

        return FlRuTask(
            id=task_id,
            title=self._get_tag_text(soup.select_one("h1.text-1")),
            url=f"{self.base_url}{path}",
            description=self._get_tag_text(soup.select_one(f"div#projectp{task_id}")),
            views=None,
            responses=responses,
            posted_at=datetime.strptime(
                self._get_tag_text(soup.select_one("div.b-layout__txt.mt-32 .text-5"))[:18], r"%d.%m.%Y | %H:%M"
            ).replace(tzinfo=ZoneInfo("Europe/Moscow")),
            price=price,
            min_price=min_price,
            max_price=max_price,
            price_type=price_type,
            author=author,
            raised=raised,
            deadline=self._get_tag_text(soup.select("div.text-right div.text-4>span")[-1]),
            safe_deal=soup.select_one("div.text-4 a[href=\"/promo/bezopasnaya-sdelka/\"]") is not None,
            self_employed_only=soup.select_one("span.b-post__bold>svg[width=\"14\"]") is not None,
            urgent=soup.select_one("span.text-10>svg[width=\"20\"]") is not None
        )