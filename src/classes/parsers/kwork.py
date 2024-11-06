import re
import asyncio
import json
from typing import AsyncGenerator, Dict, Any
from datetime import datetime
from zoneinfo import ZoneInfo

from .bs4 import BS4PlatformParser
from ..tasks import KworkTask, KworkTaskAuthor, PriceType
from ..tasks.kwork import TaskAttachment


STATE_DATA_RE = re.compile(r"window\.stateData ?= ?(?P<state_data>{.+})")

class KworkParser(BS4PlatformParser):
    name: str = "kwork.ru"
    base_url: str = "https://kwork.ru"

    async def _parse_tasks(self) -> AsyncGenerator[KworkTask, None]:
        page = 1
        while True:
            soup = await self._get_page_soup(f"/projects?page={page}")
            await asyncio.sleep(self.request_delay_seconds)

            state_data = None
            for script in soup.select("head script:not([src])"):
                if (match := STATE_DATA_RE.search(script.text)) is not None:
                    state_data = json.loads(match.group("state_data"))
            
            pagination = state_data["wantsListData"]["pagination"]
            for task_json in pagination["data"]:
                yield self._json_to_task(task_json)

            if page == pagination["last_page"]:
                break
            page+=1

    def _json_to_task(self, task_json: Dict[str, Any]) -> KworkTask:
        
        author = KworkTaskAuthor(
            name=task_json["user"]["username"],
            tasks_posted=task_json["user"]["data"]["wants_count"],
            hired_percent=task_json["user"]["data"]["wants_hired_percent"]
        )

        attachments = [
            TaskAttachment(filename=file_json["fname"], url=file_json["url"])
            for file_json in task_json["files"]
        ]

        return KworkTask(
            id=task_json["id"],
            title=task_json["name"],
            url=f"{self.base_url}/projects/{task_json['id']}/view",
            description=task_json["description"],
            views=int(task_json["views_dirty"]),
            responses=int(task_json["kwork_count"]),
            posted_at=datetime.strptime(
                task_json["date_create"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=ZoneInfo("Europe/Moscow")),
            expire_at=datetime.strptime(
                task_json["date_expire"], "%Y-%m-%d %H:%M:%S"
            ).replace(tzinfo=ZoneInfo("Europe/Moscow")),
            price=int(float(task_json["priceLimit"])) if not task_json["isHigherPrice"] else None,
            price_type=PriceType.PER_PROJECT,
            author=author,
            preffered_max_price=int(float(task_json["priceLimit"])) if task_json["isHigherPrice"] else None,
            acceptable_max_price=int(task_json["possiblePriceLimit"]) if task_json["isHigherPrice"] else None,
            attachments=attachments
        )