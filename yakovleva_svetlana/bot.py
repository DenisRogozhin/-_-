# -*- coding: utf-8 -*-

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import pandas as pd

TXT_greet = "Привет! Я - чат-бот, созданный, чтобы помочь с выбором настольной игры. Начинаем!"
TXT_party = "Давайте подберем вам игру! Сколько игроков будет играть?"
TXT_err_party_1 = "Простите, но в игру должен играть хотя бы 1 игрок... That's how game works..."
TXT_err_party_2 = "Многовато... Сейчас зависну..."
TXT_time = "Как долго вы бы хотели, чтобы продлилась одна партия (в минутах)?"
TXT_err_time_1 = 'Простите, но если вы не хотите играть, то я абсолютно беспомощен :"c'
TXT_err_time_2 = "Попробуйте D&D или другие НРИ, партии в них могут длиться вечно! А вообще, не более 5 часов фиксируется в базе данных."
TXT_lvl = "Вы готовы бросить вызов судьбе? По пятибальной шкале, насколько сложной должна быть игра?"
TXT_tags = "Хм... Позвольте узнать побольше о ваших предпочтениях... Выберите то, что для вас важно, если предпочтений несколько - напишите мне их все одним сообщением:"
TXT_redo = "\nЕще попытка?"
TXT_err_ = "Что-то я не очень понимаю... Введите еще раз, пожалуйста..."
TXT_err_fatal = "Ой-ей, что-то пошло не так! Лучше текстом..."
TXT_no = "Простите, в моей базе на данный момент нет ни одной игры, удовлетворяющей вашим запросам :с\nНо мы можем начать все сначала...\n(команда begin)"
TXT_no_2 = "Моя база все еще не пополнилась... Давайте не будем о грустном и начнем все сначала? (команда begin)"
TXT_yes = "Есть отличные результаты! Плюс в чат раскроет новый вариант, а 'хватит' == горшочек не вари :х"
TXT_find = "Хорошо! Вот, что я нашел:"
TXT_more_1 = "Что скажете? У меня есть еще варианты, если интересно."
TXT_more_2 = "Я сочту это за плюсик? Наверное? Будьте внимательнее :)"
TXT_end = "На этом все. Я могу еще что-нибудь посоветовать? (команда begin)"
TXT_not_best = "Как так, в моей неидеальной базе нет идеальной игры для вас, но посоветовать все же кое-что я могу. Но у вас отличный вкус, вот что я думаю!\nОдно сообщение, и мы продолжим. А для перезапуска есть команда begin"

def party_select(games, n):
    games = games[games['p_min'] <= n]
    games = games[games['p_max'] >= n]
    return games
    
def time_select(games, t):
    games = games[games['t_min'] <= t]
    games = games[games['t_max'] >= t]
    return games

def lvl_select(games, l):
    new = pd.concat([games[games['lvl'] == l-1],
                     games[games['lvl'] == l+1]], ignore_index=True).sample(frac=1)
    return pd.concat([games[games['lvl'] == l], new], ignore_index=True)

def tag_select(games, tags):
    for t in tags:
        games = games[games.tag.map(lambda x: t in x)]
    return games

def make_stars(l):
    return ''.join(['☆' for _ in range(l)])

def get_best(game):
    name = game['name'].to_list()[0]
    t_min = int(game['t_min'])
    t_max = int(game['t_max'])
    p_min = int(game['p_min'])
    p_max = int(game['p_max'])
    l = make_stars(int(game['lvl']))
    t = game['tag'].to_list()[0]    
    ann = game['annotation'].to_list()[0]
    
    return f'Игра {name}\nНа {t_min}-{t_max} минут\nДля {p_min}-{p_max} игроков\nСложность: {l}\nЖанр: {t}\n\nОписание:\n{ann}'


with open("TOKEN") as f:
    TOKEN = f.read()

class BotStates(StatesGroup):
    start_state = State()
    waiting_party = State()
    waiting_time = State()
    waiting_lvl = State()
    waiting_tags = State()
    result_state = State()
    no_result_state = State()



def main():

    bot = Bot(token = TOKEN)
    dp = Dispatcher(bot, storage = MemoryStorage())

    lvl_name = {"очень легкий":1, "легкий":2, "средний":3, "сложный":4, "очень сложный":5}
    tags = ["стратегия", "детектив", "сюжетные", "викторина", "подвижные",
            "социальные", "карточные", "командные", "творческие", "реиграбельные"] # предпочтения    
    
    df = pd.read_csv("games.csv") # БД с играми
    games = None                  # подходящие под запрос игры
    

    @dp.message_handler(commands=['start'], state = '*')
    async def send_welcome(msg: types.Message):
        """
        Обработчик команды `/start`
        """
        await msg.reply(TXT_greet)
        global games
        games = df.copy(deep=True)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        await msg.answer(TXT_party, reply_markup = keyboard)
        await BotStates.waiting_party.set()

    @dp.message_handler(commands=['begin'], state = '*')
    async def beginning(msg: types.Message):
        """
        Обработчик команды `/begin`
        """
        global games
        games = df.copy(deep=True)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        await msg.answer(TXT_party, reply_markup = keyboard)
        await BotStates.waiting_party.set()


    @dp.message_handler()
    async def prestart_message(msg: types.Message):
        await msg.answer("Пожалуйста, введите /start")

    @dp.message_handler(state=BotStates.waiting_party)
    async def set_party(msg: types.Message):
        """
        Обработчик количества игроков
        """
        global games
        party = 0
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard = True)
        try:
            party = int(msg.text)
        except ValueError:
            await msg.answer(TXT_err_, reply_markup = keyboard)
        else:
            if party < 1:
                await msg.answer(TXT_err_party_1 + TXT_redo, reply_markup = keyboard)
            elif party > 100:
                await msg.answer(TXT_err_party_2 + TXT_redo, reply_markup = keyboard)
            else:
                games = party_select(games, party)
                if not games.empty:
                    await msg.answer(TXT_time, reply_markup = keyboard)
                    await BotStates.waiting_time.set()
                else:
                    await msg.answer(TXT_no, reply_markup = keyboard)
                    await BotStates.no_result_state.set()
            
    @dp.message_handler(state=BotStates.waiting_time)
    async def set_time(msg: types.Message):
        """
        Обработчик времени одной партии
        """        
        global games
        time = 0
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        try:
            time = int(msg.text)
        except ValueError:
            await msg.answer(TXT_err_, reply_markup = keyboard)
        else:
            if time < 1:
                await msg.answer(TXT_err_time_1 + TXT_redo, reply_markup = keyboard)
            elif time > 300:
                await msg.answer(TXT_err_time_2 + TXT_redo, reply_markup = keyboard)
            else:
                games = time_select(games, time)
                if not games.empty:
                    buttons = list(lvl_name.keys())
                    keyboard.add(*buttons)                 
                    await msg.answer(TXT_lvl, reply_markup = keyboard)
                    await BotStates.waiting_lvl.set()
                else:
                    await msg.answer(TXT_no, reply_markup = keyboard)
                    await BotStates.no_result_state.set()          
      
    @dp.message_handler(state=BotStates.waiting_lvl)
    async def set_lvl(msg: types.Message):
        """
        Обработчик уровня сложности
        """        
        global games
        lvl = 0
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        try:
            lvl = lvl_name[msg.text.lower()]
        except:
            try:
                if int(msg.text) in lvl_name.values():
                    lvl = int(msg.text)
            except:
                await msg.answer(TXT_err_, reply_markup = keyboard)
        
        if lvl:
            games = lvl_select(games, lvl)
            if not games.empty:
                buttons = tags + ['нет предпочтений']
                keyboard.add(*buttons)
                await msg.answer(TXT_tags, reply_markup = keyboard)
                await BotStates.waiting_tags.set()
            else:
                await msg.answer(TXT_no, reply_markup = types.ReplyKeyboardRemove())
                await BotStates.no_result_state.set()                
            
    @dp.message_handler(state=BotStates.waiting_tags)
    async def set_tags(msg: types.Message):        
        """
        Обработчик тэгов
        """        
        global games
        tagged = []
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for t in tags:
            if t in msg.text.lower():
                tagged.append(t)
        if msg.text.lower() == 'нет предпочтений':
            buttons = ['еще', 'хватит']
            keyboard.add(*buttons)      
            await msg.answer(TXT_yes, reply_markup = keyboard)      
            await BotStates.result_state.set()
        elif tagged:
            new = tag_select(games, tagged)
            buttons = ['еще', 'хватит']
            keyboard.add(*buttons)               
            if new.empty:               
                await msg.answer(TXT_not_best, reply_markup = keyboard)
                await BotStates.result_state.set()
            else:
                games = new            
                await msg.answer(TXT_yes, reply_markup = keyboard)
                await BotStates.result_state.set()   
        else:
            await msg.answer(TXT_err_, reply_markup = keyboard)
    
    @dp.message_handler(state=BotStates.result_state)
    async def show_results(msg: types.Message):
        """
        Обработчик вывода результатов
        """        
        global games
        game = get_best(games[0:1])
        games = games.drop([games.index[0]])
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        if msg.text.lower() == 'хватит':
            await msg.answer(TXT_end, reply_markup = types.ReplyKeyboardRemove())
            await BotStates.no_result_state.set()
        else:
            if msg.text == '+' or msg.text.lower() == 'еще':
                await msg.reply(TXT_find)
            else:
                await msg.reply(TXT_more_2)
            
            await bot.send_message(chat_id=msg.chat.id, text=game)
            if not games.empty:                
                await msg.answer(TXT_more_1, reply_markup = keyboard)
            else:
                await msg.answer(TXT_end, reply_markup = types.ReplyKeyboardRemove())
                await BotStates.no_result_state.set()                
            

    @dp.message_handler(state=BotStates.no_result_state)
    async def show_results(msg: types.Message):
        """
        Обработчик состояния "нет результатов"
        """ 
        await msg.reply(TXT_no_2, reply_markup = types.ReplyKeyboardRemove())


    @dp.message_handler(content_types=types.ContentType.ANY, state = '*')
    async def unknown_message(msg: types.Message):
        await msg.answer(TXT_err_fatal)

    executor.start_polling(dp, skip_updates=True)


if __name__ == '__main__':

    main()
