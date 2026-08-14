# EduMind AI

EduMind AI is an AI-powered education platform that connects:

- Quiz Generator
- Flashcards
- Assignment Generator
- Chat with Lecture PDFs
- Student Progress Dashboard
- Personalized Learning

The app stores learner activity in a local SQLite database, so quiz scores,
flashcard reviews, PDF questions, and assignments dynamically update the
dashboard and the personalized learning recommendations.

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env
python -m streamlit run app.py
```

Add an OpenAI key to `.env` for live AI generation:

```env
OPENAI_API_KEY=your_real_key_here
OPENAI_MODEL=gpt-4o-mini
```

Without an API key, the platform still runs with local fallback generators so
the full product can be tested.

## Data

Runtime activity is saved to:

```text
edumind_activity.sqlite3
```

This file is created automatically the first time the app runs.

## Project structure

```text
app.py                    Main Streamlit entry point and page router
edumind/config.py         App settings, paths, and navigation labels
edumind/styles.py         Shared CSS styling
edumind/storage.py        Login, SQLite database, activity events, PDF notes
edumind/ai.py             OpenAI helper and JSON parsing
edumind/generators.py     Quiz, flashcard, and assignment generators
edumind/pdf_tools.py      PDF text extraction and lecture Q&A helper
edumind/personalization.py Weak topics, strong topics, and study plan logic
edumind/ui.py             Login screen, sidebar, and page header helpers
edumind/pages/            One file per app screen
```
