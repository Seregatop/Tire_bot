from aiogram.fsm.state import State, StatesGroup


class Reg(StatesGroup):
    wait_for_diameter = State()
    wait_for_service = State()
    wait_for_additional_service = State()
    wait_for_payment_type = State()
    wait_for_discount = State()
    wait_for_price = State()
    wait_for_send = State()
