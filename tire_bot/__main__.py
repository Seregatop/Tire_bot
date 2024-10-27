import asyncio
import logging  # loguru почитать
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher

from tire_bot.admin import AdminRouter
from tire_bot.database.models import db_init
from tire_bot.handlers import UserRouter
from tire_bot.sending_to_sheets import SheetHandler

load_dotenv()

DB_URL = os.getenv('DB_URL')
TOKEN = os.getenv('TOKEN')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')


async def async_main():
    sheet = SheetHandler(service_file="client_secret.json", spreadsheet_id=SPREADSHEET_ID)
    sess = await db_init(db_url=DB_URL)

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    user = UserRouter(sess, sheet)
    user.init_handlers()

    admin = AdminRouter(sess, sheet)
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
