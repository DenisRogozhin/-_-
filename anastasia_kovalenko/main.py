# external imports
import os
import sys
from dotenv import load_dotenv
from aiogram import Bot
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# internal imports
from handlers import register_handlers


if __name__ == '__main__':
    # your directory should contain 'variables.env' file with telegram token
    dotenv_path = os.path.join(os.path.dirname(__file__), 'variables.env')
    if os.path.exists(dotenv_path):
        load_dotenv(dotenv_path)
    else:
        print("Cannot read env file with token!")
        sys.exit()
    TOKEN = os.getenv('TOKEN')
    bot = Bot(token=TOKEN)
    dispatcher = Dispatcher(bot, storage=MemoryStorage())
    register_handlers(dp=dispatcher)
    executor.start_polling(dispatcher)
