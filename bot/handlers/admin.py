from aiogram import types, Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from bot.modules.tables.form_table import upload_tg_prices
from bot.modules.input_price.format_tg_price import format_inputprice

USERS = [22738294, 443667299]


class FSMAdmin(StatesGroup):
    input1 = State()
    input2 = State()
    input3 = State()
    input4 = State()


async def cm_start_input(message: types.Message):
    if message.from_user.id in USERS:
        await FSMAdmin.input1.set()
        await message.reply('Ожидается ввод данных')


async def load_first_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input1'] = message.text
    await FSMAdmin.next()
    await message.reply('Успешно, ожидается ввод второй части')


async def load_second_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input2'] = message.text
    await FSMAdmin.next()
    await message.reply('Успешно, ожидается ввод третий части')


async def load_third_input(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input3'] = message.text
    await FSMAdmin.next()
    await message.reply('Успешно, ожидается ввод четвёртой части')


async def processing(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['input4'] = message.text

    # данные из первого телеграмм канала
    first_tg_input = data['input1'] + '\n' + data['input2']
    # данные из второго телеграмм канала
    second_tg_input = data['input3'] + '\n' + data['input4']

    # преобразуем сообщения с прайсами из тг в словарь товаров в формат название - цена
    first_tginput_dict = format_inputprice(first_tg_input)
    second_tginput_dict = format_inputprice(second_tg_input)

    upload_tg_prices(first_tginput_dict, second_tginput_dict)
    await message.reply("Обновление цен завершено.")

    await state.finish()


def register_handlers_admin(dp: Dispatcher):
    dp.register_message_handler(cm_start_input, commands='загрузить_цены', state=None)
    dp.register_message_handler(load_first_input, state=FSMAdmin.input1)
    dp.register_message_handler(load_second_input, state=FSMAdmin.input2)
    dp.register_message_handler(load_third_input, state=FSMAdmin.input3)
    dp.register_message_handler(processing, state=FSMAdmin.input4)
