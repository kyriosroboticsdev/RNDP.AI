import sqlite3
import os
from datetime import datetime

DB_FILE = "slides.db"

def initialize_db():
    if not os.path.exists(DB_FILE):
        with sqlite3.connect(DB_FILE) as conn:
            c = conn.cursor()
            c.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    full_name TEXT,
                    email TEXT
                )
            """)
            c.execute("""
                CREATE TABLE IF NOT EXISTS slides (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    title TEXT,
                    file_path TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(user_id) REFERENCES users(id)
                )
            """)
            conn.commit()
        print("[DB] Initialized database and tables.")
    else:
        print("[DB] Database already exists.")

def add_user(username: str, full_name: str, email: str):
    username = username.lower()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            INSERT OR IGNORE INTO users (username, full_name, email)
            VALUES (?, ?, ?)
        """, (username, full_name, email))
        conn.commit()
        print(f"[DB] User added or already exists: {username}")

def save_slide(username: str, title: str, file_path: str):
    username = username.lower()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id FROM users WHERE username = ?", (username,))
        result = c.fetchone()
        if result is None:
            print(f"[DB] User '{username}' not found. Cannot save slide.")
            return
        user_id = result[0]
        c.execute("""
            INSERT INTO slides (user_id, title, file_path)
            VALUES (?, ?, ?)
        """, (user_id, title, file_path))
        conn.commit()
        print(f"[DB] Slide saved for {username}: {title}")

def get_user_slides(username: str):
    username = username.lower()
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""
            SELECT s.title, s.created_at, s.file_path
            FROM slides s
            JOIN users u ON u.id = s.user_id
            WHERE u.username = ?
            ORDER BY s.created_at DESC
        """, (username,))
        rows = c.fetchall()
        print(f"[DB] Found {len(rows)} slides for {username}.")
        return rows
