from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1 = KeyboardButton('/загрузить_цены')
b2 = KeyboardButton('/помощь')

kb_admin = ReplyKeyboardMarkup(resize_keyboard=True)

kb_admin.add(b1).add(b2)
