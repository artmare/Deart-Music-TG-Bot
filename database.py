import sqlite3
from datetime import datetime, timedelta

DB_PATH = "users.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            subscription_type TEXT,
            subscription_end_date TEXT
        )
    """)
    conn.commit()
    conn.close()

def set_subscription(user_id, sub_type, end_date):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("REPLACE INTO users (user_id, subscription_type, subscription_end_date) VALUES (?, ?, ?)",
              (user_id, sub_type, end_date))
    conn.commit()
    conn.close()

def get_subscription(user_id):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT subscription_type, subscription_end_date FROM users WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    return row if row else (None, None)
