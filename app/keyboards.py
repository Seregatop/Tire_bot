from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


test_board = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='One'), KeyboardButton(text='Two')],
                                           [KeyboardButton(text='Your contact', request_contact=True)]],
                                 resize_keyboard=True,
                                 input_field_placeholder='Choose...')

keyboard_inline_new = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Новая продажа', callback_data='car')]])

keyboard_inline_post = InlineKeyboardMarkup(inline_keyboard=[[
    InlineKeyboardButton(text='Отмена', callback_data='cancel'),
    InlineKeyboardButton(text='Отправить', callback_data='send1')]])
