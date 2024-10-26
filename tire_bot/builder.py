from aiogram.types import InlineKeyboardButton, KeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from typing import Type

from tire_bot.database.models import Base
from tire_bot.database.requests import get_available


# Генерирует клавиатуры и заполняет их значениями из таблицы
async def available_kb(db_name: Type[Base]) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()
    for diameter in await get_available(db_name):
        keyboard.add(
            InlineKeyboardButton(text=diameter.name, callback_data=diameter.name)
        )
    keyboard.adjust(3)
    keyboard.row(
        InlineKeyboardButton(text="Отмена", callback_data="cancel"),
        InlineKeyboardButton(text="Назад", callback_data="back"),
    )
    return keyboard.as_markup()
