import logging
import asyncio
import os

from aiogram import Bot, Dispatcher
from aiogram.utils.i18n import I18n
from aiogram.utils.i18n.middleware import SimpleI18nMiddleware

import routers


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)

async def main():
    bot = Bot(os.getenv("BOT_TOKEN"))
    dp = Dispatcher()

    i18n = I18n(path="locales", default_locale="en", domain="messages")
    SimpleI18nMiddleware(i18n).setup(router=dp)

    dp.include_router(routers.StartFlowRouter)

    logging.warning("Starting polling")
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())