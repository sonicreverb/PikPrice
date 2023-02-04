from aiogram import types, Dispatcher
from bot.create_bot import dp, bot
from bot.keyboards import kb_admin

USERS = [22738294, 443667299]


async def cm_start(message: types.Message):
    if message.from_user.id not in USERS:
        await message.answer('Sorry, out of order')
    else:
        await message.answer('Добро пожаловать!', reply_markup=kb_admin)
        await message.answer('Руководство по использованию: \n \n'
                             '/загрузить_цены - принимает от пользователя на ввод ДВА сообщения и на основе введённых данных создаёт таблицу с ценами'

                             )


async def cm_help(message: types.Message):
    if message.from_user.id in USERS:
        await message.answer('Руководство по использованию: \n \n'
                             '/загрузить_цены - принимает от пользователя на ввод сообщение и на основе введённых данных создаёт таблицу с ценами'
                             )


# async def echo_send(message: types.Message):
#     await message.answer(message.text)


def register_handlers_client(dp: Dispatcher):
    dp.register_message_handler(cm_start, commands='start')
    dp.register_message_handler(cm_help, commands='помощь')
    # dp.register_message_handler(echo_send)
