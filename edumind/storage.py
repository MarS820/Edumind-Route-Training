import hashlib
import json
import sqlite3
from datetime import datetime
from typing import Any

import pandas as pd

from edumind.config import DB_PATH


def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds")


def connect_db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            event_type TEXT NOT NULL,
            topic TEXT,
            score REAL,
            total REAL,
            difficulty TEXT,
            payload TEXT,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS pdf_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            filename TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


DB = connect_db()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_or_login(username: str, password: str) -> tuple[bool, str]:
    username = username.strip().lower()
    if not username or not password:
        return False, "Enter both username and password."

    existing = DB.execute("SELECT * FROM users WHERE username = ?", (username,)).fetchone()
    password_hash = hash_password(password)
    if existing:
        if existing["password_hash"] != password_hash:
            return False, "That password does not match this username."
        return True, "Welcome back."

    DB.execute(
        "INSERT INTO users (username, password_hash, created_at) VALUES (?, ?, ?)",
        (username, password_hash, now_iso()),
    )
    DB.commit()
    return True, "Account created."


def add_event(
    username: str,
    event_type: str,
    topic: str | None = None,
    score: float | None = None,
    total: float | None = None,
    difficulty: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    DB.execute(
        """
        INSERT INTO events (username, event_type, topic, score, total, difficulty, payload, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            username,
            event_type,
            topic,
            score,
            total,
            difficulty,
            json.dumps(payload or {}),
            now_iso(),
        ),
    )
    DB.commit()


def get_events(username: str) -> pd.DataFrame:
    rows = DB.execute(
        "SELECT * FROM events WHERE username = ? ORDER BY created_at DESC",
        (username,),
    ).fetchall()
    if not rows:
        return pd.DataFrame(
            columns=["id", "username", "event_type", "topic", "score", "total", "difficulty", "payload", "created_at"]
        )
    df = pd.DataFrame([dict(row) for row in rows])
    df["created_at"] = pd.to_datetime(df["created_at"])
    return df


def save_pdf_note(username: str, filename: str, content: str) -> None:
    DB.execute(
        "INSERT INTO pdf_notes (username, filename, content, created_at) VALUES (?, ?, ?, ?)",
        (username, filename, content, now_iso()),
    )
    DB.commit()
