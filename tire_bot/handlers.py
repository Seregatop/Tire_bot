from datetime import datetime

from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

from tire_bot.builder import available_kb
from tire_bot.database.models import (
    AddServiceDB,
    CategoryDB,
    DiameterDB,
    DiscountDB,
    PayerDB,
    PaymentDB,
    ServiceDB,
)
from tire_bot.database.requests import (
    approximate_price,
    check_available,
    to_main_bd,
    to_pay_bd,
)
from tire_bot.keyboards import (
    keyboard_inline_new,
    keyboard_inline_new_pay,
    keyboard_inline_post,
)
from tire_bot.sending_to_sheets import send_gs_car, send_gs_pay
from tire_bot.states import Pay, Sale

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Касса-бот, /car для начала", reply_markup=ReplyKeyboardRemove()
    )


@user.callback_query(F.data == "cancel")
async def call_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()


# доработать
@user.callback_query(F.data == "back")
async def call_back(call: CallbackQuery, state: FSMContext):
    await call.message.answer(text="Пока не работает")
    # match await state.get_state():
    #     case Sale.wait_for_diameter:
    #         return
    #     case Sale.wait_for_service:
    #         await state.set_state(Sale.wait_for_diameter)
    #         await sell_call_start(call, state)
    #     case Sale.wait_for_additional_service:
    #         await state.set_state(Sale.wait_for_service)
    #         await diameter_chosen(call, state)
    #     case Sale.wait_for_payment_type:
    #         await state.set_state(Sale.wait_for_additional_service)
    #         await service_chosen(call, state)


@user.message(Command("car"))
@user.callback_query(F.data == "car")
async def sell_start(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, Message):
        await message.delete()
        await message.answer(
            "1. Выберите диаметр колеса", reply_markup=await available_kb(DiameterDB)
        )
        await state.set_state(Sale.wait_for_diameter)
    else:
        await message.message.delete_reply_markup()
        await message.message.answer(
            "1. Выберите диаметр колеса", reply_markup=await available_kb(DiameterDB)
        )
        await state.set_state(Sale.wait_for_diameter)


@user.callback_query(Sale.wait_for_diameter)
async def diameter_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(DiameterDB, call.data):
        await call.answer(text="Выберите диаметр из списка")
        return
    await state.update_data(chosen_diameter=call.data)
    await state.set_state(Sale.wait_for_service)
    await call.message.edit_text(
        text="2. Выберите услугу", reply_markup=await available_kb(ServiceDB)
    )
    await state.update_data(message_id=call.message.message_id)


@user.callback_query(Sale.wait_for_service)
async def service_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(ServiceDB, call.data):
        await call.answer(text="Выберите услугу из списка")
        return
    await state.update_data(chosen_service=call.data)
    await state.set_state(Sale.wait_for_additional_service)
    await call.message.edit_text(
        text="3. Выберите допуслугу", reply_markup=await available_kb(AddServiceDB)
    )


@user.callback_query(Sale.wait_for_additional_service)
async def additional_service_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(AddServiceDB, call.data):
        await call.answer(text="Выберите допуслугу из списка")
        return
    await state.update_data(chosen_additional_service=call.data)
    await state.set_state(Sale.wait_for_payment_type)
    await call.message.edit_text(
        text="4. Выберите оплату", reply_markup=await available_kb(PaymentDB)
    )


@user.callback_query(Sale.wait_for_payment_type)
async def payment_type_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(PaymentDB, call.data):
        await call.answer(text="Выберите тип оплаты из списка")
        return
    await state.update_data(chosen_payment_type=call.data)
    await state.set_state(Sale.wait_for_discount)
    await call.message.edit_text(
        text="5. Выберите скидку", reply_markup=await available_kb(DiscountDB)
    )


@user.callback_query(Sale.wait_for_discount)
async def discount_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(DiscountDB, call.data):
        await call.answer(text="Выберите скидку из списка")
        return
    await state.update_data(chosen_discount=call.data)
    await state.set_state(Sale.wait_for_price)
    user_data = await state.get_data()
    price = await approximate_price(user_data["chosen_service"], user_data["chosen_diameter"])
    await call.message.edit_text(
        text=f"6. Ориентировочная цена: {price}руб.\nНапишите конечную цену:"
    )


@user.message(Sale.wait_for_price)
async def price_chosen(message: Message, state: FSMContext):
    try:
        int(message.text.lower())
    except ValueError:
        await message.answer(text="Цифру без всего")
        return
    await state.update_data(chosen_price=message.text)
    await state.set_state(Sale.wait_for_send)
    user_data = await state.get_data()
    await message.delete()
    await message.bot.edit_message_text(
        text=f'Диаметр: {user_data["chosen_diameter"]}\n'
        f'Услуга: {user_data["chosen_service"]}\n'
        f'Допулсуга: {user_data["chosen_additional_service"]}\n'
        f'Вид оплаты: {user_data["chosen_payment_type"]}\n'
        f'{user_data["chosen_discount"]}% скидка\n'
        f'Сумма: {user_data["chosen_price"]} руб.\n',
        reply_markup=keyboard_inline_post,
        chat_id=message.chat.id,
        message_id=user_data["message_id"],
    )


@user.callback_query(Sale.wait_for_send, lambda c: c.data.startswith("send_"))
async def send_chosen(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    await state.clear()
    now = datetime.now()
    new_years = datetime(day=30, month=12, year=1899)
    countdown = now - new_years
    offset = int(call.data.split("_")[1])
    await send_gs_car(
        [
            int(countdown.days) - offset,
            int(countdown.days) - offset,
            int(call.message.date.month),
            str(now.time()),
            str(call.message.chat.full_name),
            call.from_user.id,
            call.from_user.username,
            user_data["chosen_diameter"],
            str(user_data["chosen_service"]),
            user_data["chosen_additional_service"],
            "",
            user_data["chosen_payment_type"],
            round(float(user_data["chosen_discount"]) / 100, 2),
            int(user_data["chosen_price"]),
        ]
    )
    await call.answer(text="Отправлено")
    await call.message.edit_reply_markup(reply_markup=keyboard_inline_new)
    print(call.message.chat.username, user_data["chosen_price"])
    await to_main_bd(
        call.from_user.username,
        call.from_user.id,
        user_data["chosen_diameter"],
        user_data["chosen_service"],
        user_data["chosen_additional_service"],
        user_data["chosen_payment_type"],
        user_data["chosen_discount"],
        user_data["chosen_price"],
    )


# Расходы---------------------------------------------------------------------------------------------------------------
@user.message(Command("pay"))
@user.callback_query(F.data == "pay")
async def pay_start(message: Message | CallbackQuery, state: FSMContext):
    if isinstance(message, Message):
        await message.delete()
        await message.answer(
            "1. Выберите категорию", reply_markup=await available_kb(CategoryDB)
        )
        await state.set_state(Pay.wait_for_category)
    else:
        await message.message.delete_reply_markup()
        await message.message.answer(
            "1. Выберите категорию", reply_markup=await available_kb(CategoryDB)
        )
        await state.set_state(Pay.wait_for_category)


@user.callback_query(Pay.wait_for_category)
async def category_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(CategoryDB, call.data):
        await call.answer(text="Выберите категорию из списка")
        return
    await state.update_data(chosen_category=call.data)
    await state.set_state(Pay.wait_for_payer)
    await call.message.edit_text(
        text="2. Кто оплатил", reply_markup=await available_kb(PayerDB)
    )
    await state.update_data(message_id=call.message.message_id)


@user.callback_query(Pay.wait_for_payer)
async def payer_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(PayerDB, call.data):
        await call.answer(text="Выберите значение из списка")
        return
    await state.update_data(chosen_payer=call.data)
    await state.set_state(Pay.wait_for_object)
    await call.message.edit_text(text="3. На что потрачено")


@user.message(Pay.wait_for_object)
async def object_chosen(message: Message, state: FSMContext):
    await state.update_data(chosen_object=message.text)
    await state.set_state(Pay.wait_for_price)
    user_data = await state.get_data()
    await message.delete()
    await message.bot.edit_message_text(
        text=f"4. Напишите стоимость",
        chat_id=message.chat.id,
        message_id=user_data["message_id"],
    )


@user.message(Pay.wait_for_price)
async def price_chosen(message: Message, state: FSMContext):
    try:
        int(message.text.lower())
    except ValueError:
        await message.answer(text="Цифру без всего")
        return
    await state.update_data(chosen_price=message.text)
    await state.set_state(Pay.wait_for_send)
    user_data = await state.get_data()
    await message.delete()
    await message.bot.edit_message_text(
        text=f'Категория: {user_data["chosen_category"]}\n'
        f'Кто платил: {user_data["chosen_payer"]}\n'
        f'На что: {user_data["chosen_object"]}\n'
        f'Стоимость: {user_data["chosen_price"]} руб.\n',
        reply_markup=keyboard_inline_post,
        chat_id=message.chat.id,
        message_id=user_data["message_id"],
    )


@user.callback_query(Pay.wait_for_send, lambda c: c.data.startswith("send_"))
async def send_chosen(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    now = datetime.now()
    new_years = datetime(day=30, month=12, year=1899)
    countdown = now - new_years
    offset = int(call.data.split("_")[1])
    await send_gs_pay(
        [
            int(countdown.days) - offset,
            user_data["chosen_category"],
            str(user_data["chosen_object"]),
            user_data["chosen_payer"],
            user_data["chosen_price"],
            now.month,
        ]
    )
    await call.answer(text="Отправлено")
    await call.message.edit_reply_markup(reply_markup=keyboard_inline_new_pay)
    print(call.message.chat.username, user_data["chosen_price"], "pay")
    await to_pay_bd(
        call.message.from_user.id,
        call.message.from_user.username,
        user_data["chosen_category"],
        user_data["chosen_payer"],
        user_data["chosen_object"],
        user_data["chosen_price"],
    )
    await state.clear()
