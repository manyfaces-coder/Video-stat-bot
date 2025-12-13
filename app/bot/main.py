import os
import asyncio
from aiogram import Bot, Dispatcher, Router, types
from aiogram.filters import CommandStart
from dotenv import load_dotenv, find_dotenv

from app.api.request_handler import to_sql, run_sql, validate_sql

router = Router()

load_dotenv(find_dotenv())
bot = Bot(token=os.getenv('BOT_TOKEN'))
dp = Dispatcher()
dp.include_router(router)


@router.message(CommandStart())
async def handle_start(message: types.Message):
    await message.answer("Привет!\nЯ Telegram-бот для аналитики по видео\n"
                         "Ты можешь задать мне любой вопрос про видео, например:\n"
                         "\nСколько видео набрало больше 100 000 просмотров за всё время?\n"
                         "\nСколько разных видео получали новые просмотры 27 ноября 2025?")


@router.message()
async def handle_question(message: types.Message):
    await bot.send_chat_action(chat_id=message.chat.id, action="typing")

    text = (message.text or "").strip() # безопасно работаем с None и убираем пробелы
    print(f"Пришло сообщение: {text} ")
    # если вдруг пользователь пишет начиная с "/", то возьмем текст
    # иначе считаем, что весь text — вопрос.
    if text.startswith("/"):
        _, _, tail = text.partition(" ")
        print(f" _, _, tail = {tail}")
        user_text = tail.strip()
    else:
        user_text = text

    if not user_text:
        return await message.answer("Задайте вопрос текстом")

    print(f"Получилось сообщение: {user_text} ")
    try:
        # to_sql синхронный => уводим в отдельный поток, чтобы не блокировать event loop
        sql = await asyncio.to_thread(to_sql, user_text)

        validate_sql(sql)

        value = await run_sql(sql)

        return await message.answer(str(value))

    except Exception as e:
        await message.answer(f"Ошибка: {e}")



async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())