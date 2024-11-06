import os
import asyncio
import logging
from datetime import datetime, timedelta, tzinfo, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from aiogram import Bot
from aiogram.utils.i18n import I18n, gettext as _
from babel import Locale

from .platform_parsers import PLATFORM_TO_PARSER
from classes.tasks import Task
from db import async_session, Platform, PlatformRepository, User, UserRepository
from utils.markups import get_open_task_markup


PARSING_INTERVAL_SECONDS = int(os.getenv("PARSING_INTERVAL_SECONDS", "90"))
PARSING_PLATFORM_INTERVAL_SECONDS = 15
SENDING_USERS_DELAY_SECONDS = 0.25
SENDING_TASKS_DELAY_SECONDS = 1
PARSING_TASKS_LIMIT = 25

log = logging.getLogger(__name__)

scheduler = AsyncIOScheduler(
    jobstores={"default": MemoryJobStore()},
    executors={"default": AsyncIOExecutor()}
)

async def parse_new_tasks(platform_name: str, bot: Bot, i18n: I18n):
    log.info(f"Parsing {platform_name}")
    parser_type = PLATFORM_TO_PARSER[platform_name]
    session = async_session()
    async with parser_type() as parser, PlatformRepository(session) as platform_rep, UserRepository(session) as user_rep:
        platform = await platform_rep.get_first(lambda sel: sel.where(Platform.name==platform_name))
        subscribed_users = await user_rep.get_all(limit=None, filter_func=lambda sel: sel.filter(~User.disabled_platforms.contains(platform)))
        user_language_codes = dict()

        tasks_parsed = 0
        new_last_mark = platform.last_time_mark or 0
        async for task in parser.parse_new_tasks(platform.last_time_mark or 0):
            tasks_parsed+=1
            log.debug(f"[{platform_name}] task parsed ({tasks_parsed}/{PARSING_TASKS_LIMIT}): {task}")
            new_last_mark = max(new_last_mark, task.posted_at_time_mark)
            if tasks_parsed >= PARSING_TASKS_LIMIT:
                break
            for user in subscribed_users:
                log.debug(f"[{platform_name}] Checking task by user {user} filters")
                try:
                    user_filters = [filter_entry.to_filter() for filter_entry in await user.awaitable_attrs.filters]
                    filters_pass = all([user_filter.filter(task) for user_filter in user_filters])
                except Exception:
                    log.exception(f"[{platform_name}] Error while processing user {user} filters for a task {task}")
                    continue
                    
                if filters_pass:
                    if user.id not in user_language_codes:
                        log.debug(f"[{platform_name}] fetching user {user} language code")
                        try:
                            member = await bot.get_chat_member(user.telegram_id, user.telegram_id)
                            user_language_codes[user.id] = member.user.language_code
                        except Exception:
                            log.exception(f"[{platform_name}] error while fetching user {user} language code")
                            continue

                    try:
                        log.debug(f"[{platform_name}] Sending task {task} to user {user}")
                        user_timezone = timezone(timedelta(minutes=user.utc_offset_minutes or 0))
                        await _send_task_to_user(
                            task, user,
                            bot, i18n,
                            user_language_codes[user.id], user_timezone 
                        )
                    except Exception:
                        log.exception(f"[{platform_name}] Error while sending task {task} to user {user}")
                        continue
                    finally:
                        await asyncio.sleep(SENDING_USERS_DELAY_SECONDS)
            await asyncio.sleep(SENDING_TASKS_DELAY_SECONDS)
        
        log.debug(f"[{platform_name}] last_time_mark updated: {platform.last_time_mark} -> {new_last_mark}")
        platform.last_time_mark = new_last_mark
        await platform_rep.commit()
    log.debug(f"Parsing {platform_name} finished")

async def schedule_platforms_parsing(bot: Bot, i18n: I18n):
    start_datetime = datetime.now()+timedelta(seconds=PARSING_PLATFORM_INTERVAL_SECONDS)

    for platform_name in PLATFORM_TO_PARSER:
        log.debug(f"Scheduling {platform_name} parsing")
        scheduler.add_job(
            parse_new_tasks,
            "interval",
            args=(platform_name, bot, i18n),
            seconds=PARSING_INTERVAL_SECONDS,
            start_date=start_datetime
        )
        start_datetime+=timedelta(seconds=PARSING_PLATFORM_INTERVAL_SECONDS)

    scheduler.start()

async def _send_task_to_user(
        task: Task, user: User,
        bot: Bot, i18n: I18n,
        language_code: str, timezone: tzinfo
):
    language = Locale.parse(language_code, sep='-').language
    if language not in i18n.available_locales:
            language = i18n.default_locale

    with i18n.context(), i18n.use_locale(language):
        await bot.send_message(
            user.telegram_id,
            _("Hey Boss, i have a new task for you:\n\n{task}").format(task=task.translated_str(timezone)),
            reply_markup=get_open_task_markup(task.url),
            parse_mode="HTML"
        )