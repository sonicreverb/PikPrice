from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

storage = MemoryStorage()
bot = Bot(token='5684030729:AAGfgfdRwxLNmpMbI7aXQUFwEDf_9CY1qEA')
dp = Dispatcher(bot, storage=storage)
