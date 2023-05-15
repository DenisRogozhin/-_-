import os
import sys
import emoji
import random
from dotenv import load_dotenv

from aiogram import Bot, types
from aiogram.utils import executor
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

from utils.math_database import MathDatabase
from utils.math_solver import MathSolver
from utils.math_plot import MathPlot


BUTTONS = ['задай задачи из базы', 'реши мне задачу', 'построй графики функций']
POS_ANSWERS = ['Правильно!', 'Все верно!', 'Супер!', 'Верно. Молодец!', 'Отлично!', 'Абсолютно точно!', 'Да!']
NEG_ANSWERS = ['Не верно...', 'Неправильно.', 'Неправильный ответ.', 'Что-то не так.', 'Нет.']

math_database = MathDatabase()
math_solver = MathSolver()
math_plot = MathPlot()


env_file = '.env'
dotenv_path = os.path.join(os.path.dirname(__file__), env_file)
if not os.path.exists(dotenv_path):
    sys.stderr(f'There is no enviroment file "{env_file}" with token')
    sys.exit()

load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    choose_category = State()
    test_math = State()
    solve_math = State()
    plot_math = State()


def parse(text: str):
    return ' '.join(text.lower().strip().split())

@dp.message_handler(commands=['help'], state='*')
async def process_help_command(message: types.Message):
    answer = """
/start - начало работы
/exit - выход в главное меню
/help - список команд
    """
    await bot.send_message(message.from_user.id, answer)

@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply(f"Приветствую Тебя! Я математический бот {emoji.emojize(':input_numbers:')}.")
    answer = "Выбирай, какой опцией хочешь воспользоваться."
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTONS
    keyboard.add(*buttons)
    math_database.reset_choices(); math_plot.clear_plot()
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()

@dp.message_handler(commands=['exit'])
async def process_exit_command(message: types.Message):
    await message.reply(f"Возвращаю в главное меню.")
    answer = "Выбирай, какой опцией хочешь воспользоваться."
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = BUTTONS
    keyboard.add(*buttons)
    math_database.reset_choices(); math_plot.clear_plot()
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()
    
@dp.message_handler()
async def echo_message(message: types.Message):
    answer = "Введите команду /start."
    await bot.send_message(message.from_user.id, answer)

@dp.message_handler(state=BotStates.waiting_state)
async def start_work(message: types.Message):
    text = parse(message.text)
    if text in BUTTONS[0]:
        answer = 'Выбирай категорию задач.'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = math_database.get_possible_categories()
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.choose_category.set()
    elif text in BUTTONS[1]:
        answer = 'Я пока только учусь решать математические задачи. \
Поэтому могу решать лишь следующие подобные задачи: "(2 + 4) * 20 - 2/4", "x = 2+2^8-2/2", приведение подобных слагаемых.\n\
Пожалуйста, введите свою задачу.'
        keyboard = types.ReplyKeyboardRemove()
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.solve_math.set()
    elif text in BUTTONS[2]:
        answer = 'Введи уравнение графика функции в виде: y = x + 2, или q = w^2 + 2w - 1.'
        keyboard = types.ReplyKeyboardRemove()
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.plot_math.set()
    else:
        answer = f"Я тебя не понимаю {emoji.emojize(':crying_face:')}, \
не могу обработать это сообщение или еще не умею такое делать."
        answer += "\nПожалуйста, выбери из предложенных вариантов."
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = BUTTONS
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

@dp.message_handler(state=BotStates.choose_category)
async def choose_math_category(message: types.Message):
    text = parse(message.text)
    if text in math_database.get_possible_categories() or text == 'назад':
        if text == 'назад':
            math_database.del_last_choice()
        else:
            math_database.add_choice(text)
        buttons = math_database.get_possible_categories()
        if isinstance(buttons, str):
            category = buttons
            math_problem = math_database.get_problem(category)
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ['хочу другую', 'назад']
            keyboard.add(*buttons)
            await bot.send_message(message.from_user.id, math_problem, reply_markup=keyboard)
            await BotStates.test_math.set()
        else:
            if not math_database.curr_choices:
                answer = 'Выбирай категорию задач.'
            else:
                answer = f'Выбирай подкатегорию задач "{math_database.get_choices()}".'
                buttons.append('назад')
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.add(*buttons)
            await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    else:
        answer = f"Я тебя не понимаю {emoji.emojize(':crying_face:')}, \
не могу обработать это сообщение или не знаю такой категории."
        answer += "\nПожалуйста, выбери из предложенных вариантов."
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = math_database.get_possible_categories()
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

@dp.message_handler(state=BotStates.test_math)
async def test_math_problems(message: types.Message):
    text = parse(message.text)
    if text == 'назад':
        math_database.del_last_choice()
        buttons = math_database.get_possible_categories()
        if not math_database.curr_choices:
            answer = 'Выбирай категорию задач.'
        else:
            answer = f'Выбирай подкатегорию задач "{math_database.get_choices()}".'
            buttons.append('назад')
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.choose_category.set()
        return
    if text == 'хочу другую':
        answer = math_database.get_problem()
    else:
        answer = math_database.get_answer(text)
        if answer != text:
            answer = random.choice(NEG_ANSWERS) + ' Попробуй еще раз.'
        else:
            answer = random.choice(POS_ANSWERS)
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['хочу другую', 'назад']
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

@dp.message_handler(state=BotStates.solve_math)
async def solve_math_problems(message: types.Message):
    text = parse(message.text)
    answer = math_solver.solve(text)
    if answer == 'ERROR':
        answer = f'К сожалению, я еще не умею такое решать {emoji.emojize(":frowning_face:")}.'
    else:
        answer = f'Ответ: {answer}'
    keyboard = types.ReplyKeyboardRemove()
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)

@dp.message_handler(state=BotStates.plot_math)
async def plot_graphics(message: types.Message):
    text = parse(message.text)
    keyboard = types.ReplyKeyboardRemove()
    img_path = math_plot.plot(text, math_solver)
    if img_path == 'ERROR':
        answer = f'К сожалению, я еще не умею строить такие графики {emoji.emojize(":frowning_face:")}.'
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    else:
        await bot.send_photo(message.from_user.id, photo=open('path', 'rb'))

@dp.message_handler(state='*', content_types=types.ContentType.ANY)
async def process_unknown_message(message: types.Message):
    await message.answer(f"Я тебя не понимаю {emoji.emojize(':crying_face:')}, не могу обработать это сообщение.")


if __name__ == '__main__':
    executor.start_polling(dp)
