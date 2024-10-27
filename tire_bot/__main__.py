import asyncio
import logging  # loguru почитать
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from tire_bot.admin import admin
from tire_bot.database.models import db_init
from tire_bot.handlers import user


async def async_main():
    await db_init()
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()
    dp.include_routers(user, admin)
    await dp.start_polling(bot)


def main():
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Exit")


if __name__ == "__main__":
    main()
