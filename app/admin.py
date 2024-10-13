from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Filter, Command
from aiogram.fsm.context import FSMContext

from app.database.requests import season_total, day_total, admin_list

from app.sending_to_sheets import get_season, get_day

from app.states import Sale
# from app.database.requests import

admin = Router()


class Admin(Filter):
    async def __call__(self, message: Message):
        return message.from_user.id in await admin_list()


@admin.message(Admin(), Command('info'))
async def cmd_info(message: Message, state: FSMContext):
    db_result = await season_total()
    google_result = await get_season()
    await message.answer(f'Локальные данные\nОборот за сезон: р.{db_result}\n\n'
                         f'Данные из Google\nОборот за сезон: {google_result}')


@admin.message(Admin(), Command('day'))
async def cmd_day(message: Message, state: FSMContext):
    await state.clear()
    db_result = await day_total()
    google_result = await get_day()
    await message.answer(f'Локальные данные\nОборот за день: р.{db_result}\n\n'
                         f'Данные из Google\nОборот за день: {google_result}')
