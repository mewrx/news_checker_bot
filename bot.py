import asyncio
import random
import time
from os import getenv
from parser import check_news_update

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor

TOKEN = getenv("BOT_TOKEN")
chat_id = getenv("ADMIN_ID")

bot = Bot(token=TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot)


async def startup(_):
    print(time.strftime("[%H:%M] ") + "Bot is online")


async def news_checker():
    while True:
        fresh_news = check_news_update()
        if fresh_news:
            for v in fresh_news.items():
                link = v[1]["Post_link"]
                title = v[1]["Title"]
                mssg = f'<a href="{link}">{title}</a>'
                await bot.send_message(chat_id, mssg)
        print(time.strftime("[%H:%M] ") + "Чекер пройшов одне коло")
        await asyncio.sleep(random.randint(1200,3600))


@dp.message_handler(commands=['start'])
async def process_start_command(message: types.Message):
    await message.reply("Привет!\nНапиши мне что-нибудь!")


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply("Напиши мне что-нибудь, и я отпрпавлю этот текст тебе в ответ!")


@dp.message_handler(commands=['test'])
async def process_start_command(message: types.Message):
    try:
        pass
    except:
        await bot.send_message(message.from_user.id, "Щось пішло не так ( •_•)")


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
    executor.start_polling(dp, skip_updates=True, on_startup=startup)
