import json
import os
import re
from typing import Any

import streamlit as st

from edumind.config import GROQ_MODEL

try:
    from groq import Groq
except Exception:  # pragma: no cover - optional at runtime
    Groq = None


def ai_client() -> Any | None:
    if Groq is None:
        return None
    api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    if not api_key:
        return None
    return Groq(api_key=api_key)

def call_ai(system: str, user: str, max_tokens: int = 900) -> str | None:
    client = ai_client()
    if client is None:
        return None
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
            temperature=0.45,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ""
    except Exception as exc:
        st.warning(f"AI service unavailable, using local fallback. Details: {exc}")
        return None


def extract_json_list(text: str | None) -> list[dict[str, Any]] | None:
    if not text:
        return None
    match = re.search(r"\[[\s\S]*\]", text)
    if not match:
        return None
    try:
        value = json.loads(match.group(0))
        return value if isinstance(value, list) else None
    except json.JSONDecodeError:
        return None
