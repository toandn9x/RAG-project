import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from src.core.rag_engine import rag_engine

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("WARNING: TELEGRAM_BOT_TOKEN not found in .env")

bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    await message.reply("Xin chào! Tôi là chatbot RAG của bạn. Hãy gửi câu hỏi về tài liệu trong dự án, tôi sẽ trả lời dựa trên dữ liệu đó.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
        
    # Show typing status
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Query the RAG engine with session_id (chat id)
        session_id = f"tg_{message.chat.id}"
        answer = rag_engine.query(message.text, session_id=session_id)
        await message.answer(answer)
    except Exception as e:
        await message.answer(f"Có lỗi xảy ra: {str(e)}")

async def main():
    if not bot:
        print("Telegram Bot token is missing. Bot will not start.")
        return
    print("Telegram Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
