import sqlite3
import os
import json
from datetime import datetime

class ChatDatabase:
    def __init__(self, db_path="chroma_db/chat_history.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db()

    def init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT,
                    role TEXT,
                    content TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()

    def add_message(self, session_id, role, content):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (session_id, role, content) VALUES (?, ?, ?)",
                (session_id, role, content)
            )
            conn.commit()

    def get_history(self, session_id, limit=10):
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute(
                "SELECT role, content FROM messages WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
                (session_id, limit)
            )
            history = cursor.fetchall()
            # Return in chronological order
            return history[::-1]

    def clear_history(self, session_id):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
            conn.commit()

db = ChatDatabase()
