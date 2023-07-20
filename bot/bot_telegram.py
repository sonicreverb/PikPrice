from aiogram.utils import executor
from create_bot import dp
from handlers import client
from handlers import admin


def run_bot():
    admin.register_handlers_admin(dp)
    client.register_handlers_client(dp)
    executor.start_polling(dp, skip_updates=True)
