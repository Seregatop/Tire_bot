from aiogram.types import InlineKeyboardButton, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from tire_bot.database.requests import get_available


async def available_kb(db_name):
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
