from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from src.udpipe import Model
from src.train_model import Classifier


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    lemma_state = State()
    cut_down_state = State()
    tonality_state = State()
    more_info_state = State()


class UDPipeBot:
    TOKEN = '6299008004:AAErm1ncfIqzwLzOm0zfoGVcNHG6LJAN8mE'
    dp = Dispatcher(Bot(token=TOKEN), storage=MemoryStorage())

    def __init__(self, model: Model, classifier: Classifier):
        self.bot = Bot(token=self.TOKEN)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())
        self.model = model
        self.classifier = classifier

    @dp.message_handler(commands=['help'], state='*')
    async def process_help_command(self, message: types.Message):
        answer = """
            /start - начало работы
            /exit - выход в меню выбора
        """
        await self.bot.send_message(message.from_user.id, answer)

    @dp.message_handler(commands=['start'])
    async def process_start_command(self, message: types.Message):
        init_msg = """
            Привет! Я бот, который поможет разобраться с UDPipe.

            Вот что умею:
            1) Сократить текст, оставить только главные слова
            2) Лемматизировать текст
            3) Определить тональность текста 
            4) Подсказать как устроены мои команды
        """
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Сокращение", "Лемматизация", "Тональность", "Подробнее"]
        keyboard.add(*buttons)
        await self.bot.send_message(message.from_user.id, init_msg, reply_markup=keyboard)
        await BotStates.waiting_state.set()

    @dp.message_handler()
    async def echo_message(self, message: types.Message):
        answer = "Введите /start"
        await self.bot.send_message(message.from_user.id, answer)

    @dp.message_handler(commands=['exit'], state=BotStates.lemma_state)
    @dp.message_handler(commands=['exit'], state=BotStates.cut_down_state)
    @dp.message_handler(commands=['exit'], state=BotStates.tonality_state)
    @dp.message_handler(commands=['exit'], state=BotStates.more_info_state)
    async def process_exit_command(self, message: types.Message):
        answer = "Хотите перейти к сокращению, лемматизации, тональности или узнать подробности моей работы?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Сокращение", "Лемматизация", "Тональность", "Подробнее"]
        keyboard.add(*buttons)
        await self.bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.waiting_state.set()

    @dp.message_handler(state=BotStates.waiting_state)
    async def choose_type(self, message: types.Message, state: FSMContext):
        text = message.text
        if text not in ["Сокращение", "Лемматизация", "Тональность", "Подробнее"]:
            answer = "Кажется, я не понял"
            await self.bot.send_message(message.from_user.id, answer)
            answer = "Хотите перейти к сокращению, лемматизации, тональности или узнать подробности моей работы?"
            keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
            buttons = ["Сокращение", "Лемматизация", "Тональность", "Подробнее"]
            keyboard.add(*buttons)
            await self.bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        elif text == "Сокращение":
            answer = "Действительно интересная особенность UDPipe. Введите текст: "
            await self.bot.send_message(message.from_user.id, answer)
            await BotStates.cut_down_state.set()
        elif text == "Лемматизация":
            answer = "Механизм UDPipe, никакого PyMorphy. Введите текст: "
            await self.bot.send_message(message.from_user.id, answer)
            await BotStates.lemma_state.set()
        elif text == "Тональность":
            answer = "Определение тональности текста с помощью простых методов ML. Введите текст: "
            await self.bot.send_message(message.from_user.id, answer)
            await BotStates.tonality_state.set()
        elif text == "Подробнее":
            answer = "Сейчас расскажу"
            await self.bot.send_message(message.from_user.id, answer)
            await BotStates.more_info_state.set()

    @dp.message_handler(state=BotStates.cut_down_state)
    async def cut_down(self, message: types.Message, state: FSMContext):
        words = message.text.split()
        words = [lemmatize(word) for word in words]
        answer = ' '.join(words)
        await self.bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.lemmatize_state.set()

    @dp.message_handler(state=BotStates.stemming_state)
    async def stemming(self, message: types.Message, state: FSMContext):
        words = message.text.split()
        words = [ps.stem(word) for word in words]
        answer = ' '.join(words)
        await self.bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.stemming_state.set()

    @dp.message_handler(content_types=types.ContentType.ANY, state='*')
    async def unknown_message(self, msg: types.Message):
        await self.bot.send_message(msg.from_user.id, 'Я умею отвечать только на текстовые сообщения!')

    def run(self):
        executor.start_polling(self.dp)
