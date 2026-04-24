import os
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from dotenv import load_dotenv
from src.core.rag_engine import rag_engine, logger

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN not found in .env")

bot = Bot(token=TOKEN) if TOKEN else None
dp = Dispatcher()

@dp.message(Command("start"))
async def send_welcome(message: types.Message):
    logger.info(f"User {message.from_user.username} started the bot.")
    await message.reply("Xin chào! Tôi là chatbot RAG của bạn. Hãy gửi câu hỏi về tài liệu trong dự án, tôi sẽ trả lời dựa trên dữ liệu đó.")

@dp.message()
async def handle_message(message: types.Message):
    if not message.text:
        return
        
    logger.info(f"Received message from {message.from_user.username}: {message.text}")
    # Show typing status
    await bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Query the RAG engine with session_id (chat id)
        session_id = f"tg_{message.chat.id}"
        answer = rag_engine.query(message.text, session_id=session_id)
        await message.answer(answer)
        logger.info(f"Sent response to {message.from_user.username}")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await message.answer(f"Có lỗi xảy ra: {str(e)}")

async def main():
    if not bot:
        logger.error("Telegram Bot token is missing. Bot will not start.")
        return
    logger.info("Telegram Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
