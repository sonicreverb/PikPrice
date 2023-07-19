from aiogram import types, Dispatcher
# from bot.create_bot import dp, bot
from bot.keyboards import kb_admin

USERS = [22738294, 443667299]


async def cm_start(message: types.Message):
    if message.from_user.id not in USERS:
        await message.answer('Sorry, out of order')
    else:
        await message.answer('Добро пожаловать!', reply_markup=kb_admin)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands='start')
