import os
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()

APP_DIR = Path(__file__).resolve().parent.parent
DB_PATH = APP_DIR / "edumind_activity.sqlite3"
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")

FEATURES = [
    "Overview",
    "Quiz Generator",
    "Flashcards",
    "Assignment Generator",
    "Chat with Lecture PDFs",
    "Student Progress Dashboard",
    "Personalized Learning",
]
