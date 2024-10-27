import asyncio
import os
import typer

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from tire_bot.admin import AdminRouter
from tire_bot.database.requests import DatabaseHandler
from tire_bot.handlers import UserRouter
from tire_bot.sending_to_sheets import SheetHandler

load_dotenv()


def typer_main(db_url: str = typer.Option(..., envvar="DB_URL"),
               token: str = typer.Option(..., envvar="TOKEN"),
               spreadsheet_id: str = typer.Option(..., envvar="SPREADSHEET_ID")):
    db = DatabaseHandler(db_url)
    asyncio.run(db.create_all())

    sheet = SheetHandler(
        service_file="client_secret.json", spreadsheet_id=spreadsheet_id
    )

    bot = Bot(token=token)
    dp = Dispatcher()

    user = UserRouter(db, sheet)
    user.init_handlers()

    admin = AdminRouter(db, sheet)
    admin.init_handlers()

    dp.include_routers(user, admin)
    asyncio.run(dp.start_polling(bot))


def main():
    typer.run(typer_main)
    # try:
    #     asyncio.run(async_main())
    # except KeyboardInterrupt:
    #     print("Exit")


if __name__ == "__main__":
    main()
