import logging
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import SimpleI18nMiddleware

import routers
from utils.parsing.platform_parsers import init_platforms_db
from utils.parsing.background_task import schedule_platforms_parsing


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=os.getenv("LOG_LEVEL", "WARNING")
)

async def on_bot_startup(bot: Bot, i18n: I18n):
    await init_platforms_db()
    await schedule_platforms_parsing(bot, i18n)

async def main():
    bot = Bot(os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="en", domain="messages")
    SimpleI18nMiddleware(i18n).setup(router=dp)

    dp.include_router(routers.StartFlowRouter)
    dp.include_router(routers.FiltersFlowRouter)
    dp.include_router(routers.PlatformsFlowRouter)

    await on_bot_startup(bot, i18n)

    logging.warning("Starting polling")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())