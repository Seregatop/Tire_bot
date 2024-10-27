from datetime import datetime
from typing import Type

from aiogram import F, Router
from aiogram.filters import Command, Filter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.ext.asyncio import AsyncSession

from tire_bot.database.models import PaymentDB, Base
from tire_bot.database.requests import DatabaseHandler
from tire_bot.keyboards import keyboard_inline_new_fast
from tire_bot.my_router import MyRouter
from tire_bot.sending_to_sheets import SheetHandler
from tire_bot.states import FastSale


class AdminRouter(MyRouter):
    async def admin_filter(self, message: Message):
        return message.from_user.id in await self.db.admin_list()

    def init_handlers(self):
        @self.message(self.admin_filter, Command("info"))
        async def cmd_info(message: Message, state: FSMContext):
            if await state.get_state():
                user_data = await state.get_data()
                await message.bot.edit_message_reply_markup(
                    chat_id=message.chat.id,
                    message_id=user_data["message_id"],
                    reply_markup=None,
                )
            await state.clear()
            db_result = await self.db.season_total()
            google_result = await self.sheet.get_season()
            await message.answer(
                f"Локальные данные\nОборот за сезон: р.{db_result}\n\n"
                f"Данные из Google\nОборот за сезон: {google_result}"
            )

        @self.message(self.admin_filter, Command("day"))
        async def cmd_day(message: Message, state: FSMContext):
            if await state.get_state():
                user_data = await state.get_data()
                await message.bot.edit_message_reply_markup(
                    chat_id=message.chat.id,
                    message_id=user_data["message_id"],
                    reply_markup=None,
                )
            await state.clear()
            db_result = await self.db.day_total()
            google_result = await self.sheet.get_day()
            await message.answer(
                f"Локальные данные\nОборот за день: р.{db_result}\n\n"
                f"Данные из Google\nОборот за день: {google_result}"
            )

        @self.message(self.admin_filter, Command("fast"))
        @self.callback_query(self.admin_filter, F.data == "fast_car")
        async def cmd_fast(message: Message | CallbackQuery, state: FSMContext):
            if await state.get_state():
                user_data = await state.get_data()
                await message.bot.edit_message_reply_markup(
                    chat_id=message.chat.id,
                    message_id=user_data["message_id"],
                    reply_markup=None,
                )
            await state.clear()
            if isinstance(message, Message):
                await message.delete()
                await message.answer(
                    "1. Выберите тип оплаты", reply_markup=await self.available_kb(PaymentDB)
                )
            else:
                await message.message.delete_reply_markup()
                await message.message.answer(
                    "1. Выберите тип оплаты", reply_markup=await self.available_kb(PaymentDB)
                )
            await state.set_state(FastSale.wait_for_payment_type)

        @self.callback_query(FastSale.wait_for_payment_type)
        async def payment_type_chosen(call: CallbackQuery, state: FSMContext):
            if not await self.db.check_available(PaymentDB, call.data):
                await call.answer(text="Выберите тип оплаты из списка")
                return
            await state.update_data(chosen_payment_type=call.data)
            await state.set_state(FastSale.wait_for_price)
            await call.message.edit_text(text="2. Напишите конечную цену")
            await state.update_data(message_id=call.message.message_id)

        @self.message(FastSale.wait_for_price)
        async def price_chosen(message: Message, state: FSMContext):
            try:
                int(message.text.lower())
            except ValueError:
                await message.answer(text="Цифру без всего")
                return
            await state.update_data(chosen_price=message.text)
            user_data = await state.get_data()
            await state.clear()
            await message.delete()
            now = datetime.now()
            new_years = datetime(day=30, month=12, year=1899)
            countdown = now - new_years
            await self.sheet.send_gs_car(
                [
                    int(countdown.days),
                    int(countdown.days),
                    int(message.date.month),
                    str(now.time()),
                    str(message.chat.full_name),
                    message.from_user.id,
                    message.from_user.username,
                    "",
                    "",
                    "",
                    "",
                    user_data["chosen_payment_type"],
                    "",
                    int(user_data["chosen_price"]),
                ]
            )
            print(message.chat.username, user_data["chosen_price"])
            await self.db.to_main_bd(
                user_name=message.from_user.username,
                tg_id=message.from_user.id,
                diameter="Не задан",
                service="Не задан",
                additional_service="Не задан",
                payment_type=user_data["chosen_payment_type"],
                discount="Не задан",
                price=user_data["chosen_price"],
            )
            await message.bot.edit_message_text(
                text=f"Отправлено!\n"
                f'Вид оплаты: {user_data["chosen_payment_type"]}\n'
                f'Сумма: {user_data["chosen_price"]} руб.\n',
                reply_markup=keyboard_inline_new_fast,
                chat_id=message.chat.id,
                message_id=user_data["message_id"],
            )
