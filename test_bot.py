import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from app.config import config

bot = Bot(
    token=config.BOT_TOKEN,
    base_url=config.WORKER_URL,
)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_cmd(message: types.Message):
    await message.answer("✅ Бот получил команду /start!")
    print(f"Получено сообщение: {message.text}")

@dp.message()
async def all_messages(message: types.Message):
    await message.answer(f"Ты написал: {message.text}")
    print(f"Получено: {message.text}")

async def main():
    await bot.delete_webhook()
    print("⏳ Ожидаем сообщения...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())