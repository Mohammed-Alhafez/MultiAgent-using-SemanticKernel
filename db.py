import sqlite3
from typing import List, Tuple

DB_PATH = "tasks.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee TEXT NOT NULL,
                description TEXT NOT NULL,
                due_date TEXT,
                status TEXT DEFAULT 'pending'
            )
        """)
        conn.commit()

def execute_query(query: str, params: Tuple = (), fetch: bool = False) -> List[Tuple]:
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        if fetch:
            return cursor.fetchall()
        return []
