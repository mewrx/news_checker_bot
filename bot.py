from ast import Str
import asyncio
import os
import random
import time
from os import getenv
from parser import check_news_update

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from db_map import Base, UsersIds

TOKEN = getenv("BOT_TOKEN")
chat_id = getenv("ADMIN_ID")
DB_FILENAME = getenv("DB_FILENAME")

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def db_initial():
    engine = create_engine(f'sqlite:///{DB_FILENAME}')
    if not os.path.isfile(f'./{DB_FILENAME}'):
        Base.metadata.create_all(engine)
    iss = Session(bind=engine)
    return iss


async def setup_new_user(user: types.User):
    """
    Set user into `users.db` if `user.id` has no there.

    Returns `True` if added new user.
    """
    session = await db_initial()
    if not session.query(UsersIds).filter(UsersIds.user_id == user.id).first():
        user_data = UsersIds(
        user_id = user.id,
        username = user.username,
        first_name = user.first_name,
        last_name = user.last_name,
        is_bot = user.is_bot,
        language_code = user.language_code,
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
    for u in session.query(UsersIds).all():
        await bot.send_message(u.user_id, msg)


async def news_checker():
    while True:
        fresh_news = check_news_update()
        if fresh_news:
            for v in fresh_news.items():
                link = v[1]["Post_link"]
                title = v[1]["Title"]
                mssg = f'<a href="{link}">{title}</a>'
                await send_for_all(mssg)
        print(time.strftime("[%H:%M] ") + "Чекер пройшов одне коло")
        await asyncio.sleep(random.randint(1200,3600))


@dp.message_handler(commands=['start'])
async def process_start_command(msg: types.Message):
    await msg.answer("***********************")
    if await setup_new_user(msg.from_user):
        await msg.answer("Привіт!\nЯк тільки появляться свіжі новини, я зразу поділюсь з тобою.")
    else:
        await msg.answer("Привіт! З поверненням.")


@dp.message_handler(commands=['help'])
async def process_help_command(msg: types.Message):
    await msg.answer("Привіт!\nЯк тільки появляться свіжі новини, я зразу поділюсь з тобою.")


@dp.message_handler(commands=['news'])
async def process_start_command(message: types.Message):
    try:
        fresh_news = check_news_update()
        if len(fresh_news) >= 1:
            for v in fresh_news.items():
                link = v[1]["Post_link"]
                title = v[1]["Title"]
                await bot.send_message(message.from_user.id, link)
    except:
        await bot.send_message(message.from_user.id, "Щось пішло не так ( •_•)")


@dp.message_handler()
async def echo_message(msg: types.Message):
    # await bot.send_message(msg.from_user.id, msg.text)
    # Всі повідомлення перенаправляти не треба, можуть ламанути
    # escape_md() і quote_html() з aiogram.utils.markdown можуть екранувати такі символи
    pass

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.create_task(news_checker())
    executor.start_polling(dp, skip_updates=True)
