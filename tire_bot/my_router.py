from typing import Type

from aiogram import Router
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from tire_bot.database.models import Base
from tire_bot.database.requests import DatabaseHandler
from tire_bot.sending_to_sheets import SheetHandler


class MyRouter(Router):
    def __init__(self, db: DatabaseHandler, sheet: SheetHandler):
        super().__init__()
        self.db = db
        self.sheet = sheet

    async def available_kb(self, db_name: Type[Base]) -> InlineKeyboardMarkup:
        keyboard = InlineKeyboardBuilder()
        for diameter in await self.db.get_available(db_name):
            keyboard.add(
                InlineKeyboardButton(text=diameter.name, callback_data=diameter.name)
            )
        keyboard.adjust(3)
        keyboard.row(
            InlineKeyboardButton(text="Отмена", callback_data="cancel"),
            InlineKeyboardButton(text="Назад", callback_data="back"),
        )
        return keyboard.as_markup()
