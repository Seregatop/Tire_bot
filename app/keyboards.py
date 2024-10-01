from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton


test_board = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='One'), KeyboardButton(text='Two')],
                                           [KeyboardButton(text='Your contact', request_contact=True)]],
                                 resize_keyboard=True,
                                 input_field_placeholder='Choose...')



