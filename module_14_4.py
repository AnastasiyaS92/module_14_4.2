from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton,
                           InlineKeyboardMarkup, InlineKeyboardButton)
import asyncio
from crud_functions import *


api = "#"
bot = Bot(token=api)
dp = Dispatcher(bot, storage=MemoryStorage())


class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


start_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Рассчитать'),
            KeyboardButton(text='Информация')
        ],
        [KeyboardButton(text='Купить')]
    ], resize_keyboard=True
)

catalog_kb = InlineKeyboardMarkup(row_width=4)
button1 = InlineKeyboardButton(text='Product1', callback_data='product_buying')
button2 = InlineKeyboardButton(text='Product2', callback_data='product_buying')
button3 = InlineKeyboardButton(text='Product3', callback_data='product_buying')
button4 = InlineKeyboardButton(text='Product4', callback_data='product_buying')
catalog_kb.add(button1, button2, button3, button4)


@dp.message_handler(commands='start')
async def start(message):
    await message.answer(f'Привет! Я бот помогающий Вашему здоровью.\n'
                         f'Чтобы начать, нажмите "Рассчитать"', reply_markup=start_menu)


@dp.message_handler(text='Рассчитать')
async def set_age(message):
    await message.answer('Введите свой возраст:')
    await UserState.age.set()


@dp.message_handler(state=UserState.age)
async def set_growth(message, state):
    await state.update_data(age=message.text)
    await message.answer(f'Введите свой рост:')
    await UserState.growth.set()


@dp.message_handler(state=UserState.growth)
async def set_weight(message, state):
    await state.update_data(growth=message.text)
    await message.answer(f'Введите свой вес:')
    await UserState.weight.set()


@dp.message_handler(state=UserState.weight)
async def send_calories(message, state):
    await state.update_data(weight=message.text)
    data = await state.get_data()
    age = int(data['age'])
    growth = int(data['growth'])
    weight = int(data['weight'])

    calories_men = 10 * weight + 6.25 * growth - 5 * age + 5
    calories_women = 10 * weight + 6.25 * growth - 5 * age - 161

    await message.answer('Расчёт произведён, посмотрите информацию', )

    @dp.message_handler(text='Информация')
    async def inform(message):
        await message.answer(f'Ваш возраст:  {age}\nВаш рост:      {growth}\nВаш вес:          {weight}\n'
                             f'Ваша норма калорий: {calories_men}, для мужчин\n    '
                             f'{calories_women}, для женщин')

    await UserState.age.set()

    @dp.message_handler(text='Купить')
    async def get_buying_list(message):
        products = get_all_products()
        for i in range(1, 5):
            with open(f'image/{i}.png', 'rb') as img:
                 await message.answer_photo(img, f'Название: Product{i} |'
                                                    f' Описание: описание {i} | Цена: {i * 100}')
            await message.answer('Выберите продукт для покупки: ', reply_markup=catalog_kb)

    @dp.callback_query_handler(text='product_buying')
    async def send_confirm_message(call):
        await call.message.answer('Вы успешно приобрели продукт!')
        await call.answer()

    await state.finish()


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

