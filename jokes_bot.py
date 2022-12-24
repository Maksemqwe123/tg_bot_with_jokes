import random

from aiogram import Bot, Dispatcher, types  # импортируем из aiogram, Bot который отвечает за инициализацию бота,
# Dispatcher который вызывает бота
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup  # инициализация кнопок
from aiogram.utils import executor  # executor который запускает бота
from parser_joke import run_tasks  # запуск парсера

bot = Bot('5846191784:AAHRbeVwS5SfmfzgSI0gFDNbOCrushXr6S8')

dp = Dispatcher(bot)

list_of_jokes = list()


@dp.message_handler(commands='start')
async def start_message(message: types.Message):
    global list_of_jokes
    await message.answer('Привет, я бот который может рассказать анекдот', reply_markup=user_kb)


@dp.callback_query_handler(text='joke_button')
async def joke_button(callback_query: types.CallbackQuery):
    global list_of_jokes
    if len(list_of_jokes) == 0:
        await bot.send_message(callback_query.from_user.id, 'Обновите базу данных анекдотов',
                               reply_markup=update_base_kb)
        await bot.answer_callback_query(callback_query.id)
    else:
        await bot.answer_callback_query(callback_query.id)
        mess = random.choice(list_of_jokes)
        await bot.send_message(callback_query.from_user.id, f'<b>{mess}</b>', parse_mode='HTML',
                               reply_markup=user_kb)


@dp.callback_query_handler(lambda callback: callback.data == 'update_db')
async def update_db(callback_query: types.CallbackQuery):
    global list_of_jokes
    try:
        list_of_jokes = await run_tasks()
        await bot.answer_callback_query(callback_query.id, 'База данных успешно обновлена', show_alert=True)
        await bot.send_message(callback_query.from_user.id, 'Хочешь получить анекдот?', reply_markup=user_kb)
    except Exception as ex:
        await bot.answer_callback_query(callback_query.id, 'Произошла ошибка', show_alert=True)
        await bot.send_message(callback_query.from_user.id, f'{repr(ex)}', reply_markup=update_base_kb)

""" ****** BUTTONS ****** """

user_kb = InlineKeyboardMarkup(resize_keybord=True)\
    .add(InlineKeyboardButton('Получить анекдот', callback_data='joke_button'))


update_base_kb = InlineKeyboardMarkup(resize_keybord=True)\
    .add(InlineKeyboardButton('Обновить базу данных', callback_data='update_db'))

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
