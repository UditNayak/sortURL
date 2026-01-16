"""Database initialization and connection management."""
import sqlite3
from typing import Generator
from contextlib import contextmanager
from src.config import settings


def init_database() -> None:
    """Initialize SQLite database with required tables."""
    conn = sqlite3.connect(settings.DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    ''')
    
    # URLs table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS urls (
            id TEXT PRIMARY KEY,
            original_url TEXT NOT NULL,
            short_code TEXT UNIQUE NOT NULL,
            custom_alias BOOLEAN DEFAULT 0,
            user_id TEXT,
            created_at TEXT NOT NULL,
            click_count INTEGER DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')
    
    # Clicks table for analytics
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clicks (
            id TEXT PRIMARY KEY,
            url_id TEXT NOT NULL,
            clicked_at TEXT NOT NULL,
            referrer TEXT,
            user_agent TEXT,
            FOREIGN KEY (url_id) REFERENCES urls(id)
        )
    ''')
    
    conn.commit()
    conn.close()


@contextmanager
def get_db_connection() -> Generator[sqlite3.Connection, None, None]:
    """Get database connection as context manager."""
    conn = sqlite3.connect(settings.DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
    finally:
        conn.close()