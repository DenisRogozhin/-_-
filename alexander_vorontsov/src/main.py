from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import pymorphy2
import nltk

# лемматизатор
lemmatizer = pymorphy2.MorphAnalyzer(lang='ru')
lemmatizer_cache = {}


# функция для лемматизации
def lemmatize(token):
    if len(token) < 4:
        return token.lower()
    if lemmatizer.word_is_known(token):
        if token not in lemmatizer_cache:
            lemmatizer_cache[token] = lemmatizer.parse(token)[0].normal_form
        return lemmatizer_cache[token]
    return token.lower()


ps = nltk.stem.SnowballStemmer('russian')

TOKEN = '6209909898:AAHGumcWyTADq8lj0x9idiOX-oTeHxVwSe8'
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    lemmatize_state = State()
    stemming_state = State()


@dp.message_handler(commands=['help'], state='*')
async def process_help_command(message: types.Message):
    answer = """
/start - начало работы
/exit - выход в главное меню
    """
    await bot.send_message(message.from_user.id, answer)


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Hello wolrd!")
    answer = "Хотите перейти к лемматизации или стеммингу?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["лемматизация", "стемминг"]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()


# любое сообщение кроме /start
@dp.message_handler()
async def echo_message(message: types.Message):
    answer = "Введите /start"
    await bot.send_message(message.from_user.id, answer)


@dp.message_handler(commands=['exit'], state=BotStates.lemmatize_state)
@dp.message_handler(commands=['exit'], state=BotStates.stemming_state)
async def process_exit_command(message: types.Message):
    answer = "Хотите перейти к лемматизации или стеммингу?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["лемматизация", "стемминг"]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()


@dp.message_handler(state=BotStates.waiting_state)
async def choose_type(message: types.Message, state: FSMContext):
    text = message.text
    if text not in ["лемматизация", "стемминг"]:
        answer = "Не понял!"
        await bot.send_message(message.from_user.id, answer)
        answer = "Хотите перейти к лемматизации или стеммингу?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["лемматизация", "стемминг"]
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    elif text == 'лемматизация':
        answer = "Введите текст для лемматизации"
        await bot.send_message(message.from_user.id, answer)
        await BotStates.lemmatize_state.set()
    else:  # stemming
        answer = "Введите текст для стемминга"
        await bot.send_message(message.from_user.id, answer)
        await BotStates.stemming_state.set()


@dp.message_handler(state=BotStates.lemmatize_state)
async def lemmatization(message: types.Message, state: FSMContext):
    words = message.text.split()
    words = [lemmatize(word) for word in words]
    answer = ' '.join(words)
    await bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
    await BotStates.lemmatize_state.set()


@dp.message_handler(state=BotStates.stemming_state)
async def stemming(message: types.Message, state: FSMContext):
    words = message.text.split()
    words = [ps.stem(word) for word in words]
    answer = ' '.join(words)
    await bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
    await BotStates.stemming_state.set()


@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def unknown_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Я умею отвечать только на текстовые сообщения!')


executor.start_polling(dp)
