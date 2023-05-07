import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup

PP_TOKEN = "b4f5cef3167463974cdc2f05deb253baad13388c"
TG_TOKEN = "6112629657:AAGvePyZIFdgB_yZA3HEn9UOm7W_fyBDp9g"
API_URL = "http://paraphraser.ru/api"

BUTTONS = ["Вектора слов", "Словоформы", "Словарные синонимы", "Сходство двух фраз", "Определение тематики"]

class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()

    syns_state1 = State()
    syns_state2 = State()
    syns_state3 = State()

    vec_state1 = State()
    vec_state2 = State()
    vec_state3 = State()

    sim_state1 = State()
    sim_state2 = State()
    sim_state3 = State()

    form_state1 = State()
    form_state2 = State()
    form_state3 = State()

    th_state1 = State()
    th_state2 = State()
    th_state3 = State()

def syns_request(query, top):

    req = {
        'token' : PP_TOKEN,
        'c' : "syns",
        'query' : query,
        'top' : min(max(1, top), 30),
        'lang' : 'ru',
        'format' : 'json',
        'forms' : 0,
        'scores' : 0
    }

    r = requests.post(API_URL, data = req)

    return r.json()["response"]["1"]["syns"]

def vec_request(query, top):

    req = {
        'token' : PP_TOKEN,
        'c' : "vector",
        'query' : query,
        'top' : min(max(1, top), 30),
        'lang' : 'ru',
        'format' : 'json',
        'forms' : 0,
        'scores' : 0
    }

    r = requests.post(API_URL, data = req)

    return r.json()["response"]["1"]["vector"]

def sim_request(query):

    req = {
        'token' : PP_TOKEN,
        'c' : "sim",
        'query' : query,
        'type' : "vector",
        'lang' : 'ru',
        'format' : 'json',
        'forms' : 0,
        'scores' : 0
    }

    r = requests.post(API_URL, data = req)

    return float(r.json()["response"]["1"]["sim"]["score"])

def form_request(query):

    req = {
        'token' : PP_TOKEN,
        'c' : "vector",
        'query' : query,
        'top' : 1,
        'lang' : 'ru',
        'format' : 'json',
        'forms' : 1,
        'scores' : 0
    }

    r = requests.post(API_URL, data = req)

    return r.json()["response"]["1"]["forms_query"]

def th_request(query):

    req = {
        'token' : PP_TOKEN,
        'c' : "wikitopic",
        'query' : query,
        'top' : 1,
        'lang' : 'ru',
        'format' : 'json',
        'forms' : 0,
        'scores' : 0
    }

    r = requests.post(API_URL, data = req)

    return r.json()["response"]["topics"]


def main():

    bot = Bot(token = TG_TOKEN)
    dp = Dispatcher(bot, storage = MemoryStorage())

    query = ""

    @dp.message_handler(commands=['start'])
    async def send_welcome(msg: types.Message):
        """
        This handler will be called when user sends `/start` or `/help` command
        """
        await msg.reply("Привет! Я настоящий Лингвист-БОТаник, и мне нужна твоя одежда, сапоги и...")
        answer = "Короче, выбери лингво-задачу, я тебе её решу:"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = BUTTONS
        keyboard.add(*buttons)
        await msg.answer(answer, reply_markup = keyboard)
        await BotStates.waiting_state.set()

    @dp.message_handler()
    async def prestart_message(msg: types.Message):
        await msg.answer("Я ещё не разогрелся для работы. Пожалуйста, введите команду /start.")

    @dp.message_handler(state=BotStates.waiting_state)
    async def start_work(msg: types.Message):
        if msg.text == "Словарные синонимы":
            await BotStates.syns_state1.set()
            await msg.answer("Хорошо, впишите слово (или фразу), для которой найти синонимы.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Вектора слов":
            await BotStates.vec_state1.set()
            await msg.answer("Хорошо, впишите слово (или фразу), для которой найти наиболее близкие варианты на основе семантической векторной модели Word2Vec.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Сходство двух фраз":
            await BotStates.sim_state1.set()
            await msg.answer("Хорошо, впишите первое слово (или фразу), для которой будет вычислено сходство.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Словоформы":
            await BotStates.form_state1.set()
            await msg.answer("Введите слово (или фразу), для которой требуется найти все словоформы. Слова в фразе рассматриваются отдельно.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Определение тематики":
            await BotStates.th_state1.set()
            await msg.answer("Введите фразу, для которого требуется определить тематику на основе данных Википедии.", reply_markup = types.ReplyKeyboardRemove())
        else:
            await msg.answer('Я умею только решать задачи! Я ботаник, а не подружка для разговора.')

    @dp.message_handler(state=BotStates.th_state1)
    async def th_first_step(msg: types.Message):
        global query
        await BotStates.th_state2.set()
        await msg.answer("Секунду...")
        query = msg.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = ["Хочу ввести новое слово/фразу", "Вернуться к выбору задачи"]
        keyboard.add(*buttons)
        await msg.answer("Вот результаты: \n" + "\n".join(th_request(query)), reply_markup = keyboard)

    @dp.message_handler(state=BotStates.th_state2)
    async def th_second_step(msg: types.Message):
        if msg.text == "Хочу ввести новое слово/фразу":
            await BotStates.th_state1.set()
            await msg.answer("Введите фразу, для которого требуется определить тематику на основе данных Википедии.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Вернуться к выбору задачи":
            await BotStates.waiting_state.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            buttons = BUTTONS
            keyboard.add(*buttons)
            await msg.answer("Выбирай задачу:", reply_markup = keyboard)


    @dp.message_handler(state=BotStates.form_state1)
    async def form_first_step(msg: types.Message):
        global query
        await BotStates.form_state2.set()
        await msg.answer("Секунду...")
        query = msg.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = ["Хочу ввести новое слово/фразу", "Вернуться к выбору задачи"]
        keyboard.add(*buttons)
        res = form_request(query)
        await msg.answer("Результаты:")
        for word, forms in res.items():
            await msg.answer(word + ": " + ", ".join(forms))
        await msg.answer("Такие дела.", reply_markup = keyboard)

    @dp.message_handler(state=BotStates.form_state2)
    async def form_second_step(msg: types.Message):
        if msg.text == "Хочу ввести новое слово/фразу":
            await BotStates.form_state1.set()
            await msg.answer("Введите слово (или фразу), для которой требуется найти все словоформы. Слова в фразе рассматриваются отдельно.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Вернуться к выбору задачи":
            await BotStates.waiting_state.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            buttons = BUTTONS
            keyboard.add(*buttons)
            await msg.answer("Выбирай задачу:", reply_markup = keyboard)


    @dp.message_handler(state=BotStates.sim_state1)
    async def sim_first_step(msg: types.Message):
        global query
        await BotStates.sim_state2.set()
        query = msg.text
        await msg.answer("Теперь введите второе слово (или фразу).")

    @dp.message_handler(state=BotStates.sim_state2)
    async def sim_second_step(msg: types.Message):
        global query
        await BotStates.sim_state3.set()
        await msg.answer("Секунду...")
        query2 = msg.text
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = ["Хочу ввести другие слова/фразы", "Вернуться к выбору задачи"]
        keyboard.add(*buttons)
        await msg.answer("Результат сходства: " + str(sim_request(query + ";" + query2)), reply_markup = keyboard)

    @dp.message_handler(state=BotStates.sim_state3)
    async def sim_third_step(msg: types.Message):
        if msg.text == "Хочу ввести другие слова/фразы":
            await BotStates.sim_state1.set()
            await msg.answer("Хорошо, впишите первое слово (или фразу), для которой будет вычислено сходство.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Вернуться к выбору задачи":
            await BotStates.waiting_state.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            buttons = BUTTONS
            keyboard.add(*buttons)
            await msg.answer("Выбирай задачу:", reply_markup = keyboard)

    @dp.message_handler(state=BotStates.vec_state1)
    async def vec_first_step(msg: types.Message):
        global query
        await BotStates.vec_state2.set()
        query = msg.text
        await msg.answer("Топ-сколько результатов вывести? Укажите число от 0 до 30.")

    @dp.message_handler(state=BotStates.vec_state2)
    async def vec_second_step(msg: types.Message):
        global query
        await BotStates.vec_state3.set()
        await msg.answer("Секунду...")
        top = int(msg.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = ["Хочу ввести новое слово/фразу", "Хочу получить другое количество", "Вернуться к выбору задачи"]
        keyboard.add(*buttons)
        await msg.answer("Вот результаты: \n" + "\n".join(vec_request(query, top)), reply_markup = keyboard)

    @dp.message_handler(state=BotStates.vec_state3)
    async def vec_third_step(msg: types.Message):
        if msg.text == "Хочу ввести новое слово/фразу":
            await BotStates.vec_state1.set()
            await msg.answer("Хорошо, впишите слово (или фразу), для которой найти наиболее близкие варианты на основе семантической векторной модели Word2Vec.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Хочу получить другое количество":
            await BotStates.vec_state2.set()
            await msg.answer("Топ-сколько результатов вывести? Укажите число от 0 до 30.")
        elif msg.text == "Вернуться к выбору задачи":
            await BotStates.waiting_state.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            buttons = BUTTONS
            keyboard.add(*buttons)
            await msg.answer("Выбирай задачу:", reply_markup = keyboard)

    @dp.message_handler(state=BotStates.syns_state1)
    async def syns_first_step(msg: types.Message):
        global query
        await BotStates.syns_state2.set()
        query = msg.text
        await msg.answer("Топ-сколько результатов вывести? Укажите число от 0 до 30.")

    @dp.message_handler(state=BotStates.syns_state2)
    async def syns_second_step(msg: types.Message):
        global query
        await BotStates.syns_state3.set()
        await msg.answer("Секунду...")
        top = int(msg.text)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        buttons = ["Хочу ввести новое слово/фразу", "Хочу получить другое количество", "Вернуться к выбору задачи"]
        keyboard.add(*buttons)
        await msg.answer("Вот результаты: " + ", ".join(syns_request(query, top)) + ".", reply_markup = keyboard)

    @dp.message_handler(state=BotStates.syns_state3)
    async def syns_third_step(msg: types.Message):
        if msg.text == "Хочу ввести новое слово/фразу":
            await BotStates.syns_state1.set()
            await msg.answer("Хорошо, впишите слово (или фразу), для которой найти синонимы.", reply_markup = types.ReplyKeyboardRemove())
        elif msg.text == "Хочу получить другое количество":
            await BotStates.syns_state2.set()
            await msg.answer("Топ-сколько результатов вывести? Укажите число от 0 до 30.")
        elif msg.text == "Вернуться к выбору задачи":
            await BotStates.waiting_state.set()
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
            buttons = BUTTONS
            keyboard.add(*buttons)
            await msg.answer("Выбирай задачу:", reply_markup = keyboard)

    @dp.message_handler(content_types=types.ContentType.ANY, state = '*')
    async def unknown_message(msg: types.Message):
        await msg.answer('Я умею только решать задачи! Я ботаник, а не подружка для разговора.')

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':

    main()

    