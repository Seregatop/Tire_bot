import asyncio
import logging  # loguru почитать

from aiogram import Bot, Dispatcher

from tire_bot.admin import AdminRouter
from tire_bot.database.models import db_init
from tire_bot.handlers import UserRouter
from dotenv import load_dotenv


load_dotenv()


async def async_main():
    sess = await db_init(db_url='???')

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    user = UserRouter(sess)
    user.init_handlers()

    admin = AdminRouter(sess)
    admin.init_handlers()

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
