# external imports
from aiogram import types
from aiogram import Dispatcher
import surrogates
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# internal imports
from common import Person, Gender, Activities, generate_recommendation


class BotStates(StatesGroup):
    start_state = State()
    waiting_person = State()
    waiting_gender = State()
    waiting_age = State()
    waiting_activities = State()


async def process_start(message: types.Message, state: FSMContext):
    """
    Processes /start command.
    """
    await message.reply(text='Привет!' + surrogates.decode('\ud83d\ude0a') +
                             'Я бот-помощник.\nПомогу с выбором подарка на день рождения!'
                             + surrogates.decode('\ud83c\udf89'))
    answer = "Кому хотите подобрать подарок?"
    async with state.proxy() as person_info:
        person_info['activities'] = set()
        person_info['age'] = None
        person_info['gender'] = None
        person_info['type'] = None
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = [pers for pers in Person]
    keyboard.add(*buttons)
    await message.answer(answer, reply_markup=keyboard)
    await BotStates.waiting_person.set()


async def process_person_type(message: types.Message, state: FSMContext):
    """
    Waits for birthday person's type and changes the state.
    """
    person_type = message.text
    if person_type in list(Person):
        async with state.proxy() as person_info:
            person_info['type'] = person_type
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [gend for gend in Gender]
        keyboard.add(*buttons)
        await message.answer('Какого пола именинник?', reply_markup=keyboard)
        await BotStates.waiting_gender.set()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [pers for pers in Person]
        keyboard.add(*buttons)
        await message.answer('Не могу распознать тип получателя. ' +
                             'Выберите, пожалуйста, из предложенных вариантов' +
                             surrogates.decode('\ud83d\ude0a'), reply_markup=keyboard)


async def process_person_gender(message: types.Message, state: FSMContext):
    """
    Waits for birthday person's gender and changes the state.
    """
    gender = message.text
    if gender in list(Gender):
        async with state.proxy() as person_info:
            person_info['gender'] = gender
        answer = 'Введите, пожалуйста, возраст именинни'
        if gender == Gender.MALE:
            answer += 'ка.'
        else:
            answer += 'цы.'
        await message.answer(answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.waiting_age.set()
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [gend for gend in Gender]
        keyboard.add(*buttons)
        await message.answer('Извините, не смог распознать ваш ответ. ' +
                             'Выберите, пожалуйста, из предложенных вариантов' +
                             surrogates.decode('\ud83d\ude04'), reply_markup=keyboard)


async def process_person_age(message: types.Message, state: FSMContext):
    """
    Waits for birthday person's age and changes the state.
    """
    try:
        age = int(message.text)
    except ValueError:
        await message.answer('Я могу распознать возраст только в виде числа. Введите еще раз, пожалуйста' +
                             surrogates.decode('\ud83d\ude0a'))
        age = None
    if age and age < 0:
        await message.answer('Возраст не может быть отрицательным' + surrogates.decode('\ud83d\ude05') +
                             '\nВведите верное число, пожалуйста' + surrogates.decode('\ud83d\ude0a'))
    elif age and age > 100:
        await message.answer('Это очень большой возраст' + surrogates.decode('\ud83d\ude2f') +
                             '\nНе думаю, что смогу помочь с выбором подарка для такого долгожителя' +
                             surrogates.decode('\ud83d\ude05') + '\nВведите другое число, пожалуйста.')
    elif age:
        async with state.proxy() as person_info:
            person_info['age'] = age
            if person_info['gender'] == Gender.MALE:
                ending = 'ка'
                pron = 'его'
            else:
                ending = 'цы'
                pron = 'её'
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [act for act in Activities][:-1] + ['stop']
        keyboard.add(*buttons)
        answer = f"Выберите, пожалуйста, увлечения именинни{ending} (если мало знаете о {pron } интересах, " \
                 f"нажмите на 'мы мало знакомы').\nЧтобы закончить ввод, отправьте сообщение 'все'/'всё' или нажмите на 'stop'."
        await message.answer(answer, reply_markup=keyboard)
        await BotStates.waiting_activities.set()


async def process_person_activities(message: types.Message, state: FSMContext):
    """
    Waits for birthday person's activities (all of them) and changes the state.
    """
    activity = message.text
    if activity.lower() in ('stop', 'все', 'всё', 'мы мало знакомы'):
        await message.answer('Вот, что я могу порекомендовать!' + surrogates.decode('\u2728'),
                             reply_markup=types.ReplyKeyboardRemove())
        async with state.proxy() as person_info:
            answer = generate_recommendation(person_info=person_info)
            person_info['activities'] = set()
            person_info['age'] = None
            person_info['gender'] = None
            person_info['type'] = None
        await message.answer(answer)
        await BotStates.start_state.set()
    elif activity in list(Activities):
        async with state.proxy() as person_info:
            if 'activities' not in person_info:
                person_info['activities'] = {activity}
            else:
                person_info['activities'].add(activity)
    else:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = [act for act in Activities][:-1] + ['stop']
        keyboard.add(*buttons)
        await message.answer('К сожалению, не смог распознать ответ. Выберите, пожалуйста, из предложенных вариантов' +
                             surrogates.decode('\ud83d\ude0a'), reply_markup=keyboard)


async def process_unknown_message(message: types.Message):
    """
    Processes all unknown messages, emojis and stickers.
    """
    await message.answer('Я могу отвечать только на текстовые сообщения, касающиеся выбора подарка' +
                         surrogates.decode('\ud83d\ude05'))


def register_handlers(dp: Dispatcher):
    """
    Function registers all handlers in bot dispatcher.
    Remember that handlers order is significant.
    """
    dp.register_message_handler(process_start, commands=['start'], state='*')
    dp.register_message_handler(process_person_type, state=BotStates.waiting_person)
    dp.register_message_handler(process_person_gender, state=BotStates.waiting_gender)
    dp.register_message_handler(process_person_age, state=BotStates.waiting_age)
    dp.register_message_handler(process_person_activities, state=BotStates.waiting_activities)
    dp.register_message_handler(process_unknown_message, state='*', content_types=types.ContentType.ANY)
