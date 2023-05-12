from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor
from dotenv import load_dotenv

import emoji
import numpy as np
import os

vis = []

vis.append("""
__________
|        |
|       
|     
|    
|       
|      
|
|
""")

vis.append("""
__________
|        |
|       ( )
|     
|    
|       
|      
|
|
""")

vis.append("""
__________
|        |
|       ( )
|      (   )
|      (   ) 
|       
|      
|
|
""")

vis.append("""
__________
|        |
|       ( )
|     /(   )
|    / (   ) 
|       
|      
|
|
""")

vis.append("""
__________
|        |
|       ( )
|     /(   )\\
|    / (   ) \\
|       
|      
|
|
""")

vis.append("""
__________
|        |
|       ( )
|     /(   )\\
|    / (   ) \\
|       / 
|      /   
|
|
""")

vis.append("""
__________
|        |
|       ( )
|     /(   )\\
|    / (   ) \\
|       / \\
|      /   \\
|
|
""")

dotenv_path = 'variables.env'
load_dotenv(dotenv_path)
TOKEN = os.getenv('TOKEN')
bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

guessed = dict()


with open('words.txt', 'r', encoding='utf-8') as f:
    all_words = f.read().split('\n')

class BotStates(StatesGroup):
    waiting_state = State()
    cows_and_ox_state = State()
    vis_state = State()
 

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
    answer = "В какую игру вы хотите сыграть?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["быки и коровы", "виселица"]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()
    
#любое сообщение кроме /start
@dp.message_handler()
async def echo_message(message: types.Message):
    answer = "Введите /start"
    await bot.send_message(message.from_user.id, answer)

      
    
@dp.message_handler(commands=['exit'], state=BotStates.vis_state)
@dp.message_handler(commands=['exit'], state=BotStates.cows_and_ox_state)
async def process_exit_command(message: types.Message):
    answer = "В какую игру вы хотите сыграть?"
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["быки и коровы", "виселица"]
    keyboard.add(*buttons)
    await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    await BotStates.waiting_state.set()

    
def pretty_print(string):
    return "".join([s + " " for s in string])
    
@dp.message_handler(state=BotStates.waiting_state)
async def choose_type(message: types.Message, state: FSMContext):    
    text =  message.text
    if text not in ["быки и коровы", "виселица"]:
        answer = "Не умею играть в такую игру!"
        await bot.send_message(message.from_user.id, answer)
        answer = "В какую игру вы хотите сыграть?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["быки и коровы", "виселица"]
        keyboard.add(*buttons)
        await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
    elif text == 'быки и коровы':
        answer = "Я загадал число из 4 цифр без повторений. Попробуйте угадать его. Введите число из 4 цифр без повторений"
        guessed[message.from_user.id] = ("".join(np.random.choice([str(i) for i in range(10)], 4, replace=False)), 0)
        await bot.send_message(message.from_user.id, answer)
        await BotStates.cows_and_ox_state.set()
    else: #other
        word = np.random.choice(all_words)
        state = "_" * len(word)
        guessed[message.from_user.id] = (word, 0, state, set())
        answer = "Я загадал слово! Попробуйте угадать его. Введите букву\n\n\n"
        answer += "слово: " + pretty_print(state) + "\n"
        answer += vis[0]
        await bot.send_message(message.from_user.id, answer)
        await BotStates.vis_state.set()

@dp.message_handler(state=BotStates.vis_state)
async def vis_handler(message: types.Message, state: FSMContext):
    guess = message.text
    secret, attempts, state, letters = guessed[message.from_user.id]
    if len(guess) == 1 and guess.isalpha():
        if guess in letters:
            answer = "Данная буква уже угадывалась!\n"
        elif guess in secret:
            letters.add(guess)
            new_state = ""
            for i in range(len(secret)):
                if secret[i] == guess:
                    new_state += guess
                else:
                    new_state += state[i]
            state = new_state
            if state == secret:
                answer = "Вы угадали слово: " + state + emoji.emojize(":brain:")
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons = ["быки и коровы", "виселица"]
                keyboard.add(*buttons)
                await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
                await BotStates.waiting_state.set()
                return
            else:
                answer = f"Откройте букву {guess}!\n"
        else: #not guessed
            attempts = attempts + 1
            if attempts == 6:
                answer = f"Вы проиграли! \nПравильный ответ <{secret}>"
                answer += vis[attempts]
                keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
                buttons = ["быки и коровы", "виселица"]
                keyboard.add(*buttons)
                await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
                await BotStates.waiting_state.set()
                return
            else:
                answer = "Не угадал!\n"
                letters.add(guess)
        answer += "Введите букву\n\n\n"
        answer += "слово: " + pretty_print(state) + "\n"
        answer += vis[attempts]
        guessed[message.from_user.id] = secret, attempts, state, letters
        await bot.send_message(message.from_user.id, answer) 
    else:
        answer = "Некорректный ввод.\n"
        answer += "Введите букву\n\n\n"
        answer += "слово: " + pretty_print(state) + "\n"
        answer += vis[attempts]
        await bot.send_message(message.from_user.id, answer) 
    
    
    
def bullscows(guess, secret):
    cows = 0
    bulls = 0
    for i in range(len(guess)):
        if guess[i] == secret[i]:
            bulls += 1
        elif guess[i] in secret:
            cows += 1        
    return bulls, cows        
        
@dp.message_handler(state=BotStates.cows_and_ox_state)
async def cows_and_ox(message: types.Message, state: FSMContext):
    guess = message.text
    if len(guess) == 4 and guess.isnumeric() and len(set(guess)) == 4:
        secret, attempts = guessed[message.from_user.id]
        if guess == secret:
            answer = f"Вы угадали! Число попыток: {attempts} попыток! " +  emoji.emojize(":brain:") + "\nВ какую игру вы хотите сыграть?"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["быки и коровы", "виселица"]
            keyboard.add(*buttons)
            await bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
            await BotStates.waiting_state.set()
        else:
            bulls, cows = bullscows(guess, secret)
            answer = emoji.emojize(":ox:") + " " + str(bulls) + "\n" + emoji.emojize(":cow:") + " " + str(cows)
            await bot.send_message(message.from_user.id, answer)
            answer = "Введите число из 4 цифр"
            await bot.send_message(message.from_user.id, answer)
    else:
        answer = "Неправильный ввод. Введите число из 4 цифр без повторений"
        await bot.send_message(message.from_user.id, answer)
    
    
@dp.message_handler(content_types=types.ContentType.ANY, state='*')
async def unknown_message(msg: types.Message):
    await bot.send_message(msg.from_user.id, 'Я умею отвечать только на текстовые сообщения!')  
    
executor.start_polling(dp)