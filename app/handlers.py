from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import CommandStart, Command

from app.builder import available_kb
from app.database.requests import check_available
from app.database.models import PaymentDB, DiameterDB, DiscountDB, AddServiceDB, ServiceDB

from app.states import Reg
from aiogram.fsm.context import FSMContext

user = Router()


@user.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer('Касса-бот, /car для начала', reply_markup=ReplyKeyboardRemove())


@user.message(Command('car'))
async def sell_start(message: Message, state: FSMContext):
    await message.delete()
    await message.answer('1. Выберите диаметр колеса', reply_markup=await available_kb(DiameterDB))
    await state.set_state(Reg.wait_for_diameter)


@user.callback_query(Reg.wait_for_diameter)
async def diameter_chosen(call: CallbackQuery, state: FSMContext):
    if await check_available(DiameterDB, call.data):
        await call.answer(text='Выберите диаметр из списка')
        return
    await state.update_data(chosen_diameter=call.data)
    await state.set_state(Reg.wait_for_service)
    await call.message.edit_text(text='2. Выберите услугу', reply_markup=await available_kb(ServiceDB))


"""
@user.callback_query(Reg.wait_for_diameter)
async def usluga_chosen(call: CallbackQuery, state: FSMContext):
    if call.data not in requests(''):
        await call.answer(text='Выберите услугу из списка')
        return
    await state.update_data(chosen_usluga=call.data)
    await OrderFood.next()
    await call.message.edit_text(text='3\\. Выберите допуслугу', reply_markup=keybord_inline_dopuslugi)


@user.callback_query(Reg.wait_for_diameter)
async def dopusluga_chosen(call: CallbackQuery, state: FSMContext):
    if call.data not in available_dopuslugi:
        await call.answer(text='Выберите допуслугу из списка')
        return
    await state.update_data(chosen_dopusluga=call.data)
    await OrderFood.next()
    await call.message.edit_text(text='4\\. Выберите оплату', reply_markup=keybord_inline_oplata)


@user.callback_query(Reg.)
async def oplata_chosen(call: CallbackQuery, state: FSMContext):
    if call.data not in available_oplata:
        await call.answer(text='Выберите тип оплаты из списка')
        return
    await state.update_data(chosen_oplata=call.data)
    await OrderFood.next()
    await call.message.edit_text(text='5\\. Выберите скидку', reply_markup=keybord_inline_skidka)


@user.callback_query(Reg.)
async def skidka_chosen(call: CallbackQuery, state: FSMContext):
    if call.data not in available_skidka:
        await call.answer(text='Выберите скидку из списка')
        return
    await state.update_data(chosen_skidka=call.data)
    await OrderFood.next()
    user_data = await state.get_data()
    primernay_czena4 = float(prices[user_data["chosen_usluga"]][user_data["chosen_diameter"]]) * (-float(user_data["chosen_skidka"]) / 100.0 + 1)
    if user_data["chosen_dopusluga"] != "Нет":
        primernay_czena4 += 200.0
    primernay_czena = int(primernay_czena4)
    await call.message.edit_text(text=f'6\\. Оренировочая цена: __{primernay_czena}руб\\.__\nНапишите конечную цену:')


@user.callback_query(Reg.)
async def czena_chosen(msg: Message, state: FSMContext):
    try:
        int(msg.text.lower())
    except ValueError:
        await msg.answer(text='Цифру без всего')
        return
    await state.update_data(chosen_czena=msg.text)
    await OrderFood.next()
    user_data = await state.get_data()
    await msg.answer(text=
                     f'Диаметр: {user_data["chosen_diameter"]}\n'
                     f'Услуга: {user_data["chosen_usluga"]}\n'
                     f'Допулсуга: {user_data["chosen_dopusluga"]}\n'
                     f'Вид оплаты: {user_data["chosen_oplata"]}\n'
                     f'{user_data["chosen_skidka"]}% скидка\n'
                     f'Сумма: {user_data["chosen_czena"]} руб\\.\n', reply_markup=keybord_inline_otpravit)


@user.callback_query(Reg.)
async def otpravka_chosen(call: CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    # дата
    #bot.answer_callback_query()
    now = datetime.now()
    new_years = datetime(day=30, month=12, year=1899)
    countdown = now - new_years
    value_range_body = {
        "range": "Import!A:A",
        "majorDimension": "ROWS",
        "values":
            [[int(countdown.days), int(countdown.days), str(call.message.date.time()), str(call.message.chat.full_name),
              call.message.from_id, call.message.chat.username, user_data["chosen_diameter"],
              str(user_data["chosen_usluga"]), user_data["chosen_dopusluga"],
              "", user_data["chosen_oplata"], int(user_data["chosen_skidka"]), int(user_data["chosen_czena"])]]

    }
    await call.answer(text="Отправлено")
    await call.message.edit_reply_markup(reply_markup=keybord_inline_new)
    request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range=range_,
                                                     valueInputOption=value_input_option,
                                                     insertDataOption=insert_data_option, body=value_range_body)
    response = request.execute()
    pprint(response)
    print(call.message.chat.username, user_data["chosen_czena"])
    await state.clear()
"""
