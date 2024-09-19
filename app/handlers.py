from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import CommandStart, CommandObject

from app.keyboards import test_inlineboard as kb

from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


class Reg(StatesGroup):
    diameter = State()
    cost = State()
    payment = State()


router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Reg.cost)
    await message.answer(f'Выбери диаметр колеса:', reply_markup=kb)


@router.message(Reg.cost)
async def get_photo(message: Message, state: FSMContext):
    await state.set_state(Reg.payment)
    await state.set_data(cost=message.)
    await message.answer(f'ID фотографии: {message.photo[-1].file_id}')
