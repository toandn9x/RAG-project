import subprocess
import sys
import os
import time

def run_command(command):
    return subprocess.Popen(command, shell=True)

if __name__ == "__main__":
    print("--- Dang khoi dong he thong Chatbot RAG ---")
    
    # 1. Start FastAPI in background
    print("- Khoi dong API Server (Cong 8000)...")
    api_proc = run_command("C:\\Users\\Admin\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe -m uvicorn src.api.server:app --host 0.0.0.0 --port 8000")
    
    # 2. Start Telegram Bot in background
    print("- Khoi dong Telegram Bot...")
    bot_proc = run_command("C:\\Users\\Admin\\AppData\\Local\\Python\\pythoncore-3.14-64\\python.exe -m src.bot.telegram_bot")
    
    print("\n--- He thong vPro da san sang! ---")
    print("- Trang chu & Chat UI: http://localhost:8000")
    print("- Trang Quan tri (Admin): http://localhost:8000/admin")
    print("- Tai lieu API (Swagger): http://localhost:8000/docs")
    print("\nNhan Ctrl+C de dung toan bo he thong.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Đang dừng hệ thống...")
        api_proc.terminate()
        bot_proc.terminate()
        print("Đã dừng.")
