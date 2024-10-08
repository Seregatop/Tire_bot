from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command

from app.builder import available_kb
from app.database.requests import check_available, approximate_price, to_bd
from app.database.models import PaymentDB, DiameterDB, DiscountDB, AddServiceDB, ServiceDB
from app.keyboards import keyboard_inline_new, keyboard_inline_post

from app.states import Reg
from aiogram.fsm.context import FSMContext
from datetime import datetime

from app.sending_to_sheets import write_row

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Касса-бот, /car для начала', reply_markup=ReplyKeyboardRemove())


@user.callback_query(F.data == 'cancel')
async def call_cancel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await state.clear()


# доработать
@user.callback_query(F.data == 'back')
async def call_back(call: CallbackQuery, state: FSMContext):
    match await state.get_state():
        case Reg.wait_for_diameter:
            return
        case Reg.wait_for_service:
            await state.set_state(Reg.wait_for_diameter)
            await sell_call_start(call, state)
        case Reg.wait_for_additional_service:
            await state.set_state(Reg.wait_for_service)
            await diameter_chosen(call, state)
        case Reg.wait_for_payment_type:
            await state.set_state(Reg.wait_for_additional_service)
            await service_chosen(call, state)


@user.message(Command('car'))
async def sell_start(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('1. Выберите диаметр колеса', reply_markup=await available_kb(DiameterDB))
    await state.set_state(Reg.wait_for_diameter)


@user.callback_query(F.data == 'car')
async def sell_call_start(call: CallbackQuery, state: FSMContext):
    await call.message.delete_reply_markup()
    await call.message.answer('1. Выберите диаметр колеса', reply_markup=await available_kb(DiameterDB))
    await state.set_state(Reg.wait_for_diameter)
    await state.update_data(DB=DiameterDB)


@user.callback_query(Reg.wait_for_diameter)
async def diameter_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(DiameterDB, call.data):
        await call.answer(text='Выберите диаметр из списка')
        return
    await state.update_data(chosen_diameter=call.data)
    await state.set_state(Reg.wait_for_service)
    await call.message.edit_text(text='2. Выберите услугу', reply_markup=await available_kb(ServiceDB))
    await state.update_data(message_id=call.message.message_id)


@user.callback_query(Reg.wait_for_service)
async def service_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(ServiceDB, call.data):
        await call.answer(text='Выберите услугу из списка')
        return
    await state.update_data(chosen_service=call.data)
    await state.set_state(Reg.wait_for_additional_service)
    await call.message.edit_text(text='3. Выберите допуслугу', reply_markup=await available_kb(AddServiceDB))


@user.callback_query(Reg.wait_for_additional_service)
async def additional_service_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(AddServiceDB, call.data):
        await call.answer(text='Выберите допуслугу из списка')
        return
    await state.update_data(chosen_additional_service=call.data)
    await state.set_state(Reg.wait_for_payment_type)
    await call.message.edit_text(text='4. Выберите оплату', reply_markup=await available_kb(PaymentDB))


@user.callback_query(Reg.wait_for_payment_type)
async def payment_type_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(PaymentDB, call.data):
        await call.answer(text='Выберите тип оплаты из списка')
        return
    await state.update_data(chosen_payment_type=call.data)
    await state.set_state(Reg.wait_for_discount)
    await call.message.edit_text(text='5. Выберите скидку', reply_markup=await available_kb(DiscountDB))


@user.callback_query(Reg.wait_for_discount)
async def discount_chosen(call: CallbackQuery, state: FSMContext):
    if not await check_available(DiscountDB, call.data):
        await call.answer(text='Выберите скидку из списка')
        return
    await state.update_data(chosen_discount=call.data)
    await state.set_state(Reg.wait_for_price)
    user_data = await state.get_data()
    price = await approximate_price(user_data['chosen_service'])
    await call.message.edit_text(text=f'6. Ориентировочная цена: {price}руб.\nНапишите конечную цену:')


@user.message(Reg.wait_for_price)
async def price_chosen(message: Message, state: FSMContext):
    try:
        int(message.text.lower())
    except ValueError:
        await message.answer(text='Цифру без всего')
        return
    await state.update_data(chosen_price=message.text)
    await state.set_state(Reg.wait_for_send)
    user_data = await state.get_data()
    await message.bot.delete_message(chat_id=message.chat.id, message_id=int(user_data['message_id']))
    await message.delete()
    await message.answer(text=
                         f'Диаметр: {user_data["chosen_diameter"]}\n'
                         f'Услуга: {user_data["chosen_service"]}\n'
                         f'Допулсуга: {user_data["chosen_additional_service"]}\n'
                         f'Вид оплаты: {user_data["chosen_payment_type"]}\n'
                         f'{user_data["chosen_discount"]}% скидка\n'
                         f'Сумма: {user_data["chosen_price"]} руб.\n', reply_markup=keyboard_inline_post)


@user.callback_query(Reg.wait_for_send)
async def send_chosen(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    now = datetime.now()
    new_years = datetime(day=30, month=12, year=1899)
    countdown = now - new_years
    await write_row(
        [int(countdown.days), int(countdown.days), int(call.message.date.month), str(call.message.date.time()),
         str(call.message.chat.full_name), call.from_user.id, call.from_user.username,
         user_data["chosen_diameter"], str(user_data["chosen_service"]), user_data["chosen_additional_service"],
         "", user_data["chosen_payment_type"], round(float(user_data["chosen_discount"]) / 100, 2),
         int(user_data["chosen_price"])])
    await call.answer(text="Отправлено")
    await call.message.edit_reply_markup(reply_markup=keyboard_inline_new)
    print(call.message.chat.username, user_data["chosen_price"])
    await to_bd(call.message.from_user.username, user_data["chosen_diameter"], user_data["chosen_service"],
                user_data["chosen_additional_service"], user_data["chosen_payment_type"], user_data["chosen_discount"],
                user_data["chosen_price"])
    await state.clear()
