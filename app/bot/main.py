import os
import asyncio
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv, find_dotenv

async def main():
    load_dotenv(find_dotenv())
    bot = Bot(token=os.getenv('TOKEN'))
    dp = Dispatcher()

    await dp.start_polling(bot)

if __name__ =="__main__":
    asyncio.run(main())