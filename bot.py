import asyncio
import itertools
import json
import logging
import os
import random
import sys
from ast import Str
from os import getenv
from parser import check_news_update

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db_map import Base, UsersIds
from decorators import is_admin

# logging.basicConfig(level=logging.INFO)
logging.basicConfig(
    filename='bot.log',
    filemode='w',
    format='%(name)s - %(levelname)s - %(message)s'
)

TOKEN = getenv("BOT_TOKEN")
chat_id = getenv("ADMIN_ID")
DB_FILENAME = getenv("DB_FILENAME")

if not TOKEN or not DB_FILENAME or not chat_id:
    sys.exit("Error: no enviroment variables provided")

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def db_initial():
    engine = create_engine(f'sqlite:///{DB_FILENAME}')
    if not os.path.isfile(f'./{DB_FILENAME}'):
        Base.metadata.create_all(engine)
    session = Session(bind=engine)
    return session


async def setup_new_user(user: types.User):
    """
    Set user into `users.db` if `user.id` has no there.

    Returns `True` if added new user.
    """
    session = await db_initial()
    if not session.query(UsersIds).filter(UsersIds.user_id == user.id).first():
        user_data = UsersIds(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            is_bot=user.is_bot,
            language_code=user.language_code,
        )
        session.add(user_data)
        session.commit()
        return True
    else:
        return False


async def send_for_all(msg: Str):
    """
    Send message for all who is in `users.db`.
    """
    session = await db_initial()
    for user in session.query(UsersIds).all():
        await bot.send_message(user.user_id, msg)


async def news_checker():
    while True:
        fresh_news = check_news_update()
        if fresh_news:
            for news in fresh_news.items():
                link = news[1]["Post_link"]
                title = news[1]["Title"]
                mssg = f'<a href="{link}">{title}</a>'
                await send_for_all(mssg)
        await asyncio.sleep(random.randint(1200, 3600))


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    if await setup_new_user(msg.from_user):
        await msg.answer("""
        Привіт! Як тільки появляться свіжі новини, зразу поділюсь ними.

        Команди:
        /help - переглянути це меню
        /last - останні три новини
        """)
    else:
        await msg.answer("Привіт! З поверненням.")


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    if chat_id == str(msg.from_user.id):
        await msg.answer("""
        Привіт! Як тільки появляться свіжі новини, зразу поділюсь ними.

        Команди:
        /help - переглянути це меню
        /last - останні три новини
        /admin - адмін-панель
        /log - вигрузити лог файл
        """)
    else:
        await msg.answer("""
        Привіт! Як тільки появляться свіжі новини, зразу поділюсь ними.

        Команди:
        /help - переглянути це меню
        /last - останні три новини
        """)


@dp.message_handler(commands=['admin'])
@is_admin
async def show_admin_panel(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    buttons = ["Розмір бази", "Вигрузити базу", "Відмінити"]
    keyboard.add(*buttons)
    await message.answer("Радий вас бачити, власник!\n", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Вигрузити базу")
@is_admin
async def get_db(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Відправляю..", reply_markup=remove_keyboard)
    await message.reply_document(open(DB_FILENAME, 'rb'))


@dp.message_handler(lambda message: message.text == "Розмір бази")
@is_admin
async def get_db_size(message: types.Message):
    session = await db_initial()
    lenght = session.query(UsersIds).count()
    await message.answer(f"{lenght} rows in data base.")


@dp.message_handler(lambda message: message.text == "Відмінити")
async def action_cancel(message: types.Message):
    remove_keyboard = types.ReplyKeyboardRemove()
    await message.answer("Як скажеш.", reply_markup=remove_keyboard)


@dp.message_handler(commands=['log'])
@is_admin
async def get_log_file(msg: types.Message):
    await msg.reply_document(open('bot.log', 'rb'))


@dp.message_handler(commands=['last'])
async def get_last_5_news(msg: types.Message):
    """
    Send 3 last news
    """
    json_path = "data/articles_dict.json"
    with open(json_path, "r", encoding="utf-8") as news:
        articles_list = json.load(news)
    for i in itertools.islice(reversed(articles_list.items()), 0, 3):
        link = i[1]["Post_link"]
        title = i[1]["Title"]
        mssg = f'<a href="{link}">{title}</a>'
        await msg.answer(mssg)

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(news_checker())
    executor.start_polling(dp, skip_updates=True)
