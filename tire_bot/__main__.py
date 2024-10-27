import asyncio
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from tire_bot.admin import AdminRouter
from tire_bot.database.requests import DatabaseHandler
from tire_bot.handlers import UserRouter
from tire_bot.sending_to_sheets import SheetHandler

load_dotenv()

DB_URL = os.getenv("DB_URL")
TOKEN = os.getenv("TOKEN")
SPREADSHEET_ID = os.getenv("SPREADSHEET_ID")


async def async_main():
    db = DatabaseHandler(DB_URL)
    await db.create_all()

    sheet = SheetHandler(
        service_file="client_secret.json", spreadsheet_id=SPREADSHEET_ID
    )

    bot = Bot(token=TOKEN)
    dp = Dispatcher()

    user = UserRouter(db, sheet)
    user.init_handlers()

    admin = AdminRouter(db, sheet)
    admin.init_handlers()

    dp.include_routers(user, admin)
    await dp.start_polling(bot)


def main():
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        print("Exit")


if __name__ == "__main__":
    main()
