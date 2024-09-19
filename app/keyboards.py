from aiogram.types import ReplyKeyboardMarkup, InlineKeyboardMarkup, KeyboardButton, InlineKeyboardButton

test_board = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='One'), KeyboardButton(text='Two')],
                                           [KeyboardButton(text='Your contact', request_contact=True)]],
                                 resize_keyboard=True,
                                 input_field_placeholder='Choose...')


test_inlineboard = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='R13', callback_data='13'),
                                                  KeyboardButton(text='R14', callback_data='14')],
                                                 [KeyboardButton(text='R15', callback_data='15')]],
                                       resize_keyboard=True)
