from aiogram import Bot, types
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.utils import executor

from src.udpipe import Model
from src.train_model import Classifier
from src.utils import pretty_print, tonality_print


class BotStates(StatesGroup):
    start_state = State()
    waiting_state = State()
    lemma_state = State()
    cut_down_state = State()
    tonality_state = State()
    more_info_state = State()


class UDPipeBot:
    def __init__(self, token: str, model: Model, classifier: Classifier):
        self.model = model
        self.classifier = classifier

        self.bot = Bot(token=token)
        self.dp = Dispatcher(self.bot, storage=MemoryStorage())

        self.process_help_command = self.dp.message_handler(commands=['help'], state='*')(self.process_help_command)
        self.process_start_command = self.dp.message_handler(commands=['start'])(self.process_start_command)
        self.echo_message = self.dp.message_handler()(self.echo_message)
        self.process_exit_command = self.dp.message_handler(commands=['exit'], state='*')(self.process_exit_command)
        self.choose_type = self.dp.message_handler(state=BotStates.waiting_state)(self.choose_type)
        self.cut_down = self.dp.message_handler(state=BotStates.cut_down_state)(self.cut_down)
        self.lemma = self.dp.message_handler(state=BotStates.lemma_state)(self.lemma)
        self.tonality = self.dp.message_handler(state=BotStates.tonality_state)(self.tonality)
        self.unknown_message = self.dp.message_handler(
            content_types=types.ContentType.ANY,
            state='*'
        )(self.unknown_message)

    async def process_help_command(self, message: types.Message):
        answer = """
            /start - начало работы
            /exit - выход в меню выбора
        """
        await self.bot.send_message(message.from_user.id, answer)

    async def process_start_command(self, message: types.Message):
        # await message.reply("Hello wolrd!")
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

    async def echo_message(self, message: types.Message):
        answer = "Введите /start"
        await self.bot.send_message(message.from_user.id, answer)

    async def process_exit_command(self, message: types.Message):
        answer = "Хотите перейти к сокращению, лемматизации, тональности или узнать подробности моей работы?"
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        buttons = ["Сокращение", "Лемматизация", "Тональность", "Подробнее"]
        keyboard.add(*buttons)
        await self.bot.send_message(message.from_user.id, answer, reply_markup=keyboard)
        await BotStates.waiting_state.set()

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

    async def cut_down(self, message: types.Message, state: FSMContext):
        response_result = self.model.get_response(message.text)
        parse_result = self.model.parse_result(response_result)
        answer = pretty_print(parse_result, "cut")
        await self.bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.cut_down_state.set()

    async def lemma(self, message: types.Message, state: FSMContext):
        response_result = self.model.get_response(message.text)
        parse_result = self.model.parse_result(response_result)
        answer = pretty_print(parse_result, "lemma")
        await self.bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.cut_down_state.set()

    async def tonality(self, message: types.Message, state: FSMContext):
        response_result = self.model.get_response(message.text)
        parse_result = self.model.parse_result(response_result)

        content = ""
        for cur_msg in parse_result['main_words']:
            content += ' '.join(cur_msg) + '. '

        mark = self.classifier.predict(content, True)

        answer = tonality_print(mark)
        await self.bot.send_message(message.from_user.id, answer, reply_markup=types.ReplyKeyboardRemove())
        await BotStates.cut_down_state.set()

    async def unknown_message(self, msg: types.Message):
        await self.bot.send_message(msg.from_user.id, 'Я умею отвечать только на текстовые сообщения!')

    def run(self):
        executor.start_polling(self.dp)
