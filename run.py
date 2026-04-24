import subprocess
import sys
import os
import time
from dotenv import load_dotenv

def run_command(command):
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    load_dotenv()
    port = os.getenv("PORT", "8000")
    
    print("--- Dang khoi dong he thong Chatbot RAG ---")
    
    # 1. Start FastAPI in background
    print(f"- Khoi dong API Server (Cong {port})...")
    api_proc = run_command(f"C:\\Users\\Admin\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe -m uvicorn src.api.server:app --host 0.0.0.0 --port {port}")
    
    # 2. Start Telegram Bot in background
    print("- Khoi dong Telegram Bot...")
    bot_proc = run_command("C:\\Users\\Admin\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe -m src.bot.telegram_bot")
    
    print("\n--- He thong vPro da san sang! ---")
    print(f"- Trang chu & Chat UI: http://localhost:{port}")
    print(f"- Trang Quan tri (Admin): http://localhost:{port}/admin")
    print(f"- Tai lieu API (Swagger): http://localhost:{port}/docs")
    print("\nNhan Ctrl+C de dung toan bo he thong.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng hệ thống...")
        api_proc.terminate()
        bot_proc.terminate()
        print("Đã dừng.")
