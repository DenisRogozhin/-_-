from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
import pandas as pd



df = pd.read_csv('Books.csv',sep=';')

epochs = ["XXI век","Вторая половина XX века","Первая половина XX века", "XIX век", "XVII – XVIII века",
                    "XV – XVI века", "до XIV века", "Античная литература"]


books = []
for i in df.index:
    book = dict()
    book['Author'] = df.Author[i]
    book['Genres'] = set(df.Genres[i].split('|'))
    book['Name'] = df.Name[i]
    book['Pages'] = int(df.Pages[i])
    book['Epoch'] = epochs[df.Epoch[i]-1]
    book['Description'] = df.Description[i]
    books.append(book)

genre =["Фэнтези",
        "Фантастика",
"Детектив",
"Приключенческая литература",
"Роман, повесть",
"Реалистическая проза",
"Сказки",
"Любовный роман",
"Исторический роман",
"Мемуары",
"Трагедия",
"Ужасы",
"Мистика",
"Поэзия"
]
epochs = ["XXI век","Вторая половина XX века","Первая половина XX века", "XIX век", "XVII – XVIII века",
                    "XV – XVI века", "до XIV века", "Античная литература"]

dotenv_path = open('Token.txt', mode='r')

TOKEN = dotenv_path.read().replace('\n','')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    choose_epoch = State()
    choose_genre = State()
    pages_state = State()
    search_book = State()
    wait_answer = State()
 

@dp.message_handler(commands=['help'], state='*')
async def process_help_command(message: types.Message):
    answer = """
/start - начало работы
    """
    await bot.send_message(message.from_user.id, answer)

@dp.message_handler(commands=['start'])
@dp.message_handler(state=BotStates.start_state)
async def process_start_command(message: types.Message):
    answer = "Добрый день! Хотите я помогу подобрать Вам книгу?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    buttons = ["Да", "Нет"]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()
    
#любое сообщение кроме /start
@dp.message_handler()
async def echo_message(message: types.Message):
    answer = "Введите /start"
    await bot.send_message(message.from_user.id, answer)

 
@dp.message_handler(state=BotStates.waiting_state)
async def choose_epoch(message: types.Message, state: FSMContext):    
    text =  message.text
    if text not in ["Да", "Нет"]:
        answer = "Не понял!"
        await bot.send_message(message.from_user.id, answer)
        answer = "Хотите я помогу подобрать Вам книгу?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Да", "Нет"]
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    elif text == 'Да':
        answer = "Книгу, написанную в какую эпоху, Вы хотите прочитать?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Любая эпоха"] + [a for a in epochs]
        async with state.proxy() as person_info:
            person_info['genre'] = set()
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.choose_epoch.set()
    else: #Завершаем работу бота
        answer = "Хорошего дня!"
        await bot.send_message(message.from_user.id, answer)
        await BotStates.start_state.set()


@dp.message_handler(state=BotStates.choose_epoch)
async def choose_genre(message: types.Message, state: FSMContext):    
    text =  message.text
    if text not in (["Любая эпоха"] + [a for a in epochs]):
        answer = "Не понял!"
        await bot.send_message(message.from_user.id, answer)
        answer = "Книгу, написанную в какую эпоху, Вы хотите прочитать?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        buttons = ["Любая эпоха"] + [a for a in epochs]
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.choose_epoch.set()
    else:
        answer = "Отличный выбор: "+ text
        async with state.proxy() as person_info:
            if text == "Любая эпоха":
                person_info['epoch'] = epochs
            else:
                person_info['epoch'] = [text]
        await bot.send_message(message.from_user.id, answer)
        answer = """Книгу, написанную в каких жанрах, Вы хотите прочитать? Выберите, пожалуйста, все интересующие Вас жанры.\nЧтобы закончить ввод, нажмите на 'stop'."""
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [a for a in genre] + ['stop']
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.choose_genre.set()


@dp.message_handler(state=BotStates.choose_genre)
async def choose_pages(message: types.Message, state: FSMContext):    
    text = message.text
    if text.lower() in ('stop'):
        answer = 'Введите, пожалуйста, максимальное количество страниц в книге, что Вы готовы прочитать:'
        await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.pages_state.set()
    elif text in genre:
        async with state.proxy() as person_info:
            if 'genre' not in person_info:
                person_info['genre'] = set([text])
            else:
                person_info['genre']= person_info['genre'] | set([text])
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [a for a in genre] + ['stop']
        keyboard.add(*buttons)
        await message.answer('К сожалению, не смог распознать ответ. Выберите, пожалуйста, из предложенных вариантов' 
                            , reply_markup=keyboard)
        

@dp.message_handler(state=BotStates.pages_state)
async def end_choose(message: types.Message, state: FSMContext):    
    try:
        pages = int(message.text)
    except ValueError:
        pages = None
        await message.answer('Я могу распознать количество страниц только в виде числа. Введите еще раз, пожалуйста')
    if pages and pages < 0:
        await message.answer('Количество страниц не может быть отрицательным' +
                             '\nВведите верное число, пожалуйста')
    elif pages:
        async with state.proxy() as person_info:
            person_info['pages'] = pages
        await BotStates.search_book.set()
        async with state.proxy() as person_info:
            a = book_rating(person_info)
            person_info['rating'] = a
            person_info['viewed'] = [0 for i in range(len(books))]
            k = book_best(person_info['rating'], person_info['viewed'])
            if k != -1:
                person_info['viewed'][k] = 1
        if k == -1:
            
            await message.answer('К сожалению, не удалось подобрать книгу с заданными параметрами, поробуйте снова.'
                            )
            await BotStates.start_state.set()
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ["Да", "Нет", "Хватит"]
            keyboard.add(*buttons)
            await message.answer('Вас заинтересует книга:\n'+
                                 'Название: '+ books[k]['Name']+'\n'+
                                 'Автор: '+ books[k]['Author']+'\n'+
                                 'Описание: '+ books[k]['Description']
                                 , reply_markup=keyboard)
            await BotStates.wait_answer.set()



@dp.message_handler(state=BotStates.wait_answer)
async def choose_epoch(message: types.Message, state: FSMContext):    
    text =  message.text
    if text not in ["Да", "Нет", "Хватит"]:
        answer = "Не понял! Ответьте, пожалуйста, Да, Нет или Хватит"
        await bot.send_message(message.from_user.id, answer)

    elif text == 'Да':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        await message.answer('Рад, что смог помочь. Хорошего дня!', reply_markup=keyboard)
        await BotStates.start_state.set()
    elif text == 'Хватит':
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        await message.answer('Хорошего дня!', reply_markup=keyboard)
        await BotStates.start_state.set()
    else: 
        async with state.proxy() as person_info:
            k = book_best(person_info['rating'], person_info['viewed'])
            if k != -1:
                person_info['viewed'][k] = 1

        if k == -1:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = []
            keyboard.add(*buttons)
            await message.answer('К сожалению, не удалось подобрать книгу с заданными параметрами, поробуйте снова.', reply_markup=keyboard)
            await BotStates.start_state.set()
        else:
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
            buttons = ["Да", "Нет", 'Хватит']
            keyboard.add(*buttons)
            await message.answer('Вас заинтересует книга:\n'+
                                 'Название: '+ books[k]['Name']+'\n'+
                                 'Автор: '+ books[k]['Author']+'\n'+
                                 'Описание: '+ books[k]['Description']
                                 , reply_markup=keyboard)
            await BotStates.wait_answer.set()
        
def book_best(rating, viewed):
    status = 0
    j = -1
    for i in range(len(rating)):
        if rating[i] > status and viewed[i] == 0:
            j = i
            status = rating[i]
    return j

def book_rating(person_info):
    status = []
    for book in books:
            if book['Epoch'] in person_info['epoch'] and book['Pages'] <= person_info['pages']:
                status.append(len(book['Genres']&person_info['genre']))
            else:
                status.append(0)
    return status



@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def unknown_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Я умею отвечать только на текстовые сообщения!')  
    
    
executor.start_polling(dp)
