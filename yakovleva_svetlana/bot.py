# -*- coding: utf-8 -*-

import requests
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
import pandas as pd

df = pd.read_csv("games.csv") # БД с играми
games_num = len(df)           # количество игор в игротеке

TXT_greet_1 = "Привет! Я - чат-бот, созданный, чтобы помочь с выбором настольной игры. Начинаем!"
TXT_greet_2 = f"""Позвольте представиться надлежащим образом...
Я владею архивом, небольшой базой данных из {games_num} игр. Буду искать в ней игры, которые больше подходят именно вам. Для этого мне придется немного пораспрашивать вас.

Также давайте условимся, что команда /begin заставит меня начать нашу беседу сначала.
Команда /help даст понять, что у вас возникли проблемы, и я постараюсь помочь.
А если вы захотите побольше узнать о моей игротеке, то воспользуйтесь командой /games"""
TXT_party = "Давайте подберем вам игру! Сколько игроков будет играть?"
TXT_party_help = "Первым вопросом я всегда спрашиваю о количестве игроков - ведь это самое важное. Здесь не получится оставить кого-то за бортом. Я жду от вас число от 1 до 100, на большее база данных не рассчитана. Однако, не могу гарантировать, что в архивах будут подобные игры. Если вас слишком много и подходящих игр нет - попробуйте поделиться на команды и написать количество команд."
TXT_err_party_1 = "Простите, но в игру должен играть хотя бы 1 игрок... That's how game works..."
TXT_err_party_2 = "Многовато... Сейчас зависну..."
TXT_time = "Как долго вы бы хотели, чтобы продлилась одна партия (в минутах)?"
TXT_time_help = 'Вторым вопросом укажите примерное время партии в минутах. В 1 часе 60 минут, если что. Я пойму любое целое число, либо же вы можете ответить "не важно", если у вас достаточно свободного времени. В базе фиксируется время партии до 5 часов.'
TXT_err_time_1 = 'Простите, но если вы не хотите играть, то я абсолютно беспомощен :"c'
TXT_err_time_2 = "Попробуйте D&D или другие НРИ, партии в них могут длиться вечно! А вообще, не более 5 часов фиксируется в базе данных."
TXT_lvl = "Вы готовы бросить вызов судьбе? По пятибальной шкале, насколько сложной должна быть игра?"
TXT_lvl_help = 'Третьи идет вопрос про сложность игры. Оценка эта сложная и по большей части зависит от ваших соперников. Однако при оценке учитывалась нагруженность игровыми механиками и возрастное ограничение, поставленное издателем. Вы можете выбрать 1 из предложенных вариантов, либо написать его в чат, либо написать число от 1 до 5. Выберите "не важно", если нет пожеланий.'
TXT_tags = "Хм... Позвольте узнать побольше о ваших предпочтениях... Выберите то, что для вас важно, если предпочтений несколько - напишите мне их все одним сообщением:"
TXT_tags_help = '''Выберите ваши предпочтения в играх, которые обязательно должны присутствовать в вашей игре. Можете выбрать из предложенного, можете написать в 1 сообщении несколько вариантов, либо выбрать "нет предпочтений". Если найдутся игры, включающие все ваши предпочтения, я их и выберу. Если же точного совпадения не будет - я покаже то, что нашел до этого.

Несколько пояснений:
Стратегия - это игры, включающие военные элементы.
Детектив - игра, в которой необходимо разгадать загадку и логически думать.
В сюжетных играх история является одним из главных игровых элементов.
Викторины - это игры, в которых нужно отвечать на вопросы, проверяющие ваш кругозор и ваши знания.
Подвижные - могут включать ктакие игровые элементы, как, например, пантомима.
Социальные - игры, в которых вам придется много взаимодействовать с другими игроками, общаться с ними.
Карточные игры основаны на характеристиках карт и чаще всего включают большой элемент случайности.
Командные - это те, в которых все игроки играют в 1 команде на благо общей победы.
Творческие - игры, развивающие творческие навыки и воображение.
В реиграбельные игры можно играть снова и снова.'''
TXT_redo = "\nЕще попытка?"
TXT_err_ = "Что-то я не очень понимаю... Введите еще раз, пожалуйста..."
TXT_err_fatal = "Ой-ей, что-то пошло не так! Лучше текстом..."
TXT_no = "Простите, в моей базе на данный момент нет ни одной игры, удовлетворяющей вашим запросам :с\nНо мы можем начать все сначала...\n(команда /begin)"
TXT_no_2 = "Моя база все еще не пополнилась... Давайте не будем о грустном и начнем все сначала? (команда /begin)"
TXT_yes = "Есть отличные результаты! Плюс в чат раскроет новый вариант, а 'хватит' == горшочек не вари :х"
TXT_yes_help = 'Выберите "еще" или напишите что угодно в чат, чтобы я показал новую подходящую вам игру. Если выберете или напишете "хватит", то я тут же остановлюсь.'
TXT_find = "Хорошо! Вот, что я нашел:"
TXT_more_1 = "Что скажете? У меня есть еще варианты, если интересно."
TXT_more_2 = "Я сочту это за плюсик? Наверное? Будьте внимательнее :)"
TXT_end = "На этом все. Я могу еще что-нибудь посоветовать? (команда /begin)"
TXT_not_best = 'Как так, в моей неидеальной базе нет идеальной игры для вас, но посоветовать все же кое-что я могу. Но у вас отличный вкус, вот что я думаю!\n"Еще" или плюск в чат, и мы продолжим. А для перезапуска есть команда /begin'
TXT_help_next = 'Нажмайте "далее", чтобы открывать больше информации обо мне. Команда /begin вернет меня к началу нашей беседы.'
TXT_help = [TXT_party_help, TXT_time_help, TXT_lvl_help, TXT_tags_help, TXT_yes_help]
TXT_archive = f"В моей игротеке целых {games_num} игр! Вот они, слева направо:"

def party_select(games, n):
    games = games[games['p_min'] <= n]
    games = games[games['p_max'] >= n]
    return games
    
def time_select(games, t):
    games = games[games['t_min'] <= t]
    games = games[games['t_max'] >= t]
    return games

def lvl_select(games, l):
    new = pd.concat([games[games['lvl'] == l-1].sample(frac=1),
                     games[games['lvl'] == l+1]], ignore_index=True).sample(frac=1)
    return pd.concat([games[games['lvl'] == l], new], ignore_index=True)

def tag_select(games, tags):
    for t in tags:
        if not games.empty:
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
    helping_state = State()
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
    
    
    games = None # подходящие под запрос игры
    h_ind = 0    # для отображения полной документации

    @dp.message_handler(commands=['start'], state = '*')
    async def send_welcome(msg: types.Message):
        """
        Обработчик команды `/start`
        """
        await msg.reply(TXT_greet_1)
        keyboard = types.ReplyKeyboardRemove()
        await bot.send_message(chat_id=msg.chat.id, text=TXT_greet_2, reply_markup = keyboard)
        await BotStates.start_state.set()       
    
    @dp.message_handler(commands=['begin'], state = '*')
    async def beginning(msg: types.Message):
        """
        Обработчик команды `/begin`
        """
        global games
        games = df.copy(deep=True)
        keyboard = types.ReplyKeyboardRemove()
        await msg.answer(TXT_party, reply_markup = keyboard)
        await BotStates.waiting_party.set()
        
    @dp.message_handler(commands=['games'], state = '*')
    async def show_games(msg: types.Message):
        """
        Обработчик команды `/games`
        """
        keyboard = types.ReplyKeyboardRemove()
        await bot.send_message(chat_id=msg.chat.id, text=TXT_archive)
        await bot.send_message(chat_id=msg.chat.id, text='\n'.join(list(df.name)))
        
    @dp.message_handler(commands=['help'], state = BotStates.start_state)
    @dp.message_handler(commands=['help'], state = BotStates.no_result_state)
    async def help(msg: types.Message):
        """
        Обработчик команды `/help`
        """
        global h_ind
        h_ind = 0
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True) 
        await bot.send_message(chat_id=msg.chat.id, text=TXT_greet_2)
        buttons = ['далее']
        keyboard.add(*buttons)
        await msg.answer(TXT_help_next, reply_markup = keyboard)
        await BotStates.helping_state.set()

    @dp.message_handler(state=BotStates.helping_state)
    async def helping(msg: types.Message):
        """
        Выдача информации о работе бота
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)        
        if msg.text.lower() == 'далее':
            try:
                global h_ind
                txt = TXT_help[h_ind]
                h_ind += 1
                await bot.send_message(chat_id=msg.chat.id, text=txt)
            except:
                await msg.answer(TXT_end, reply_markup = types.ReplyKeyboardRemove())  
        elif h_ind < len(TXT_help):
            await msg.answer(TXT_help_next, reply_markup = keyboard)
        else:
            await msg.answer(TXT_end, reply_markup = types.ReplyKeyboardRemove()) 

    @dp.message_handler(state=BotStates.start_state)
    async def starting(msg: types.Message):
        """
        Начало после перезапуска бота
        """        
        global games
        games = df.copy(deep=True)
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)    
        await msg.answer(TXT_party, reply_markup = keyboard)
        await BotStates.waiting_party.set()     

    @dp.message_handler()
    async def prestart_message(msg: types.Message):
        await msg.answer("Пожалуйста, введите /start")

    @dp.message_handler(commands=['help'], state=BotStates.waiting_party)
    async def help_party(msg: types.Message):
        """
        Помощь в определении игроков
        """
        await bot.send_message(chat_id=msg.chat.id, text=TXT_party_help)

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
                    buttons = ['не важно']
                    keyboard.add(*buttons)                    
                    await msg.answer(TXT_time, reply_markup = keyboard)
                    await BotStates.waiting_time.set()
                else:
                    await msg.answer(TXT_no, reply_markup = keyboard)
                    await BotStates.no_result_state.set()
            
    @dp.message_handler(commands=['help'], state=BotStates.waiting_time)
    async def help_time(msg: types.Message):
        """
        Помощь в определении времени
        """
        await bot.send_message(chat_id=msg.chat.id, text=TXT_time_help)
        
    
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
            if msg.text.lower() == 'не важно':
                buttons = list(lvl_name.keys()) + ['не важно']
                keyboard.add(*buttons)                 
                await msg.answer(TXT_lvl, reply_markup = keyboard)
                await BotStates.waiting_lvl.set()                
            else:
                await msg.answer(TXT_err_, reply_markup = keyboard)
        else:
            if time < 1:
                await msg.answer(TXT_err_time_1 + TXT_redo, reply_markup = keyboard)
            elif time > 300:
                await msg.answer(TXT_err_time_2 + TXT_redo, reply_markup = keyboard)
            else:
                games = time_select(games, time)
                if not games.empty:
                    buttons = list(lvl_name.keys()) + ['не важно']
                    keyboard.add(*buttons)                 
                    await msg.answer(TXT_lvl, reply_markup = keyboard)
                    await BotStates.waiting_lvl.set()
                else:
                    await msg.answer(TXT_no, reply_markup = keyboard)
                    await BotStates.no_result_state.set()          
    
    @dp.message_handler(commands=['help'], state=BotStates.waiting_lvl)
    async def help_lvl(msg: types.Message):
        """
        Помощь в определении сложности
        """
        await bot.send_message(chat_id=msg.chat.id, text=TXT_lvl_help)    
    
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
                if msg.text.lower() != 'не важно':
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
        elif msg.text.lower() == 'не важно':
            buttons = tags + ['нет предпочтений']
            keyboard.add(*buttons)
            await msg.answer(TXT_tags, reply_markup = keyboard)
            await BotStates.waiting_tags.set()

    @dp.message_handler(commands=['help'], state=BotStates.waiting_tags)
    async def help_tags(msg: types.Message):
        """
        Помощь в определении предпочтений
        """
        await bot.send_message(chat_id=msg.chat.id, text=TXT_tags_help)    
            
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

    @dp.message_handler(commands=['help'], state=BotStates.result_state)
    async def help_results(msg: types.Message):
        """
        Помощь при отображении результатов
        """
        await bot.send_message(chat_id=msg.chat.id, text=TXT_yes_help)  
    
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
    async def show_no_results(msg: types.Message):
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
