from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types

import os
import random
from datetime import datetime
from nltk import word_tokenize
import pymorphy2
import string
import json


with open('./.env', mode='r', encoding='utf-8') as env_file:
    token = env_file.read()
bot = Bot(token=token)
dp = Dispatcher(bot, storage=MemoryStorage())

workout_data = {}
curr_ex = 0


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    doing_nothing_state = State()
    wout_state = State()
    ex_state = State()


@dp.message_handler(commands=['info'], state='*')
async def print_workout_stats(message: types.Message):
    global workout_data, curr_ex

    if 'start_time' in workout_data:
        end_time = workout_data.get('end_time', datetime.now())
        wout_dur = (end_time - workout_data['start_time']).seconds
        ex_durs = []
        ex_trips = []
        for key, value in workout_data.items():
            if key.startswith('Упражнение'):
                ex_end_time = value.get('end_time', datetime.now())
                ex_durs.append((ex_end_time - value['start_time']).seconds)
                ex_trips.extend(value['Подходы'])
        avg_ex_dur = sum(ex_durs) / len(ex_durs) if len(ex_durs) > 0 else 0
        avg_ex_trips = sum(ex_trips) / len(ex_trips) if len(ex_trips) > 0 else 0

        msg = f'Всего упражнений: {curr_ex}\nОбщая продолжительность: {wout_dur // 60}m {wout_dur % 60}s\nСреднее кол-во повторений: {avg_ex_trips:.1f}\nСредняя продолжительность упражнения: {int(avg_ex_dur // 60)}m {int(avg_ex_dur % 60)}s'
        await bot.send_message(message.from_user.id, msg)
    
    else:
        msg = 'Тренировка ещё не началась.'
        await bot.send_message(message.from_user.id, msg)


@dp.message_handler(commands=['start'], state='*')
async def process_command_start(message: types.Message):
    global workout_data, curr_ex
    workout_data = {}
    curr_ex = 0
    intro = 'Привет! Меня зовут Ронни и я помогу тебе записывать прогресс на своей тренировке. Начнём?'

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Поехали!']
    keyboard.add(*buttons)

    await message.answer(intro, reply_markup=keyboard)
    await BotStates.waiting_state.set()


@dp.message_handler()
async def echo_message(message: types.Message):
    msg = 'Введите /start'
    await bot.send_message(message.from_user.id, msg)


@dp.message_handler(state=BotStates.waiting_state)        
async def process_waiting(message: types.Message):
    msg = 'Отлично! Ты можешь начать тренировку, попросить посоветовать упражнение, а также смотивировать тебя или развеселить мемасиком.'

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ['Начать тренировку']
    keyboard.add(*buttons)

    await message.answer(msg, reply_markup=keyboard)
    await BotStates.doing_nothing_state.set()


@dp.message_handler(state=BotStates.doing_nothing_state)
async def process_doing_nothing(message: types.Message):
    global workout_data, curr_ex
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == 'Начать тренировку':
        curr_ex = 0
        workout_data = {}
        st_time = datetime.now()
        msg = f'Yeaaaaahh buddy!\nНачало: {st_time.strftime("%d-%m-%Y %H:%M:%S")}'
        workout_data['start_time'] = st_time
        buttons = ['Новое упражнение', 'Закончить тренировку']
        keyboard.add(*buttons)

        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
        await BotStates.wout_state.set()

    else:
        await find_similar_action(message)


@dp.message_handler(state=BotStates.wout_state)
async def process_workout(message: types.Message):
    global workout_data, curr_ex
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text == 'Новое упражнение':
        curr_ex += 1
        st_time = datetime.now()
        workout_data[f'Упражнение №{curr_ex}'] = {'start_time': st_time, 'Подходы': []}

        msg = f'Упражнение №{curr_ex}\nНачало: {st_time.strftime("%H:%M:%S")}\nВведите количество повторений:'
        buttons = ['Закончить упражнение']
        keyboard.add(*buttons)

        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
        await BotStates.ex_state.set()

    elif message.text == 'Закончить тренировку':
        workout_data['end_time'] = datetime.now()
        dur = (workout_data['end_time'] - workout_data['start_time']).seconds
        msg = f'Тренировка закончена! Продолжительность: {dur // 60}m {dur % 60}s\nТы сегодня хорошо потрудился!'
        buttons = ['Новая тренировка']
        keyboard.add(*buttons)

        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
        await BotStates.waiting_state.set()

    else:
        await find_similar_action(message)


@dp.message_handler(state=BotStates.ex_state)
async def process_ex(message: types.Message):
    global workout_data
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)

    if message.text.isdigit():
        workout_data[f'Упражнение №{curr_ex}']['Подходы'].append(int(message.text))
        msg = 'Введите количество повторений:'
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)

    elif message.text == 'Закончить упражнение':
        end_time = datetime.now()
        start_time = workout_data[f'Упражнение №{curr_ex}']['start_time']
        dur = (end_time - start_time).seconds
        workout_data[f'Упражнение №{curr_ex}']['end_time'] = end_time
        buttons = ['Новое упражнение', 'Закончить тренировку']
        keyboard.add(*buttons)
        msg = f'Упражнение закончено. Продолжительность: {dur // 60}m {dur % 60}s'

        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)
        await BotStates.wout_state.set()

    else:
        msg = 'Во время упражнения отвлекаться нельзя!'
        await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)


@dp.message_handler(state='*', content_types=types.ContentTypes.ANY)
async def process_unknown_types(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    msg = 'Я умею отвечать только не текстовые сообщения. Напиши что-нибудь ещё.'
    await bot.send_message(message.from_user.id, msg, reply_markup=keyboard)


async def find_similar_action(message: types.Message):
    vec = await preprocess_input(message.text)

    for w in ['мем', 'шут', 'прикол']:
        if any(map(lambda x: w in x, vec)):
            pth = './memes/'
            with open(pth + random.choice(os.listdir(pth)), mode='rb') as photo:
                await bot.send_photo(message.from_user.id, photo)
            return
    
    for w in ['цитат', 'мотив']:
        if any(map(lambda x: w in x, vec)):
            mode = random.choice(['txt', 'voice'])
            if mode == 'txt':
                with open('./quotes.txt', mode='r', encoding='utf-8') as q_file:
                    msg = random.choice(list(map(lambda s: s.strip(), q_file.readlines())))
                    await bot.send_message(message.from_user.id, msg)
            else:
                pth = './voices/'
                with open(pth + random.choice(os.listdir(pth)), mode='rb') as vc:
                    await bot.send_voice(message.from_user.id, vc)
            return
        
    if any(map(lambda x: 'совет' in x, vec)) and any(map(lambda x: 'упражн' in x, vec)):
        with open('./exercises.json', mode='r', encoding='utf-8') as ex_file:
            all_exercises = json.load(ex_file)
            group = random.choice(list(all_exercises.keys()))
            ex = random.choice(all_exercises[group])
            msg = f'Упражнение на {group.lower()}: {ex}'
            await bot.send_message(message.from_user.id, msg)

    for w in ['инф', 'результ', 'статист']:
        if any(map(lambda x: w in x, vec)):
            await print_workout_stats(message)
            return


async def preprocess_input(text):
    text = text.lower()
    morph = pymorphy2.MorphAnalyzer()
    tokens = [tok for tok in word_tokenize(text, language='russian') if tok not in string.punctuation]
    lemmas = [morph.parse(tok)[0].normal_form for tok in tokens]
    return lemmas


executor.start_polling(dp)