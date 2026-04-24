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
    
    # 1. Send a temporary "pending" message so the user knows bot is working
    pending_msg = await message.reply("⏳ Đang tra cứu tài liệu và suy nghĩ...")
    
    try:
        # Show typing status
        await bot.send_chat_action(message.chat.id, "typing")
        
        # 2. Query the RAG engine in a background thread to avoid blocking the bot
        session_id = f"tg_{message.chat.id}"
        logger.info(f"Submitting query to RAG engine for session {session_id}...")
        answer = await asyncio.to_thread(rag_engine.query, message.text, session_id)
        logger.info("Received answer from RAG engine.")
        
        # 3. Edit the pending message with the final answer
        logger.info("Editing pending message on Telegram...")
        try:
            await pending_msg.edit_text(answer, parse_mode="Markdown")
        except Exception:
            # Fallback if markdown is invalid
            await pending_msg.edit_text(answer)
        logger.info(f"Sent response to {message.from_user.username}")
    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        await pending_msg.edit_text(f"❌ Có lỗi xảy ra trong quá trình xử lý: {str(e)}")

async def main():
    if not bot:
        logger.error("Telegram Bot token is missing. Bot will not start.")
        return
    logger.info("Telegram Bot is starting...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
