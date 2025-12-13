import os
import asyncio
import aiohttp
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv, find_dotenv


router = Router()


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer("Привет!")


@router.message(Command('api'))
async def handler_info(message: types.Message):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://127.0.0.1:8000/info') as resp:
                data = await resp.json()
                await message.answer(f"Ответ от API: {data}")

    except Exception as e:
        await message.answer(f"Ошибка при запросе к API: {e}")


async def main():
    load_dotenv(find_dotenv())
    bot = Bot(token=os.getenv('BOT_TOKEN'))
    dp = Dispatcher()
    dp.include_router(router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())