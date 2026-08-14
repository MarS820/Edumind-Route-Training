"""
quiz_generator.py
------------------
Pure quiz-generation logic for EduMind AI — no Streamlit, no HTML, no UI
code at all. This file only knows how to turn (topic, difficulty, n) into
a list of quiz-question dicts, either via the Groq AI model or a local
fallback bank. Import the one function you need from quiz_generator.py:

    from quiz_generator import generate_quiz

quiz_generator.generate_quiz(topic, n, difficulty, subject=None, avoid=None)
    -> List[dict], each dict shaped like:
        {"question": str, "options": [str, str, str, str],
         "correct": int, "difficulty": str, "explanation": str}
"""

import os
import random
from typing import List, Optional
import streamlit as st

from pydantic import BaseModel, Field, field_validator
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

# ------------------------------------------------------------------------
# QUIZ GENERATOR — real AI-powered generation (Groq + LangChain)
# ------------------------------------------------------------------------


class QuizQuestion(BaseModel):
    question: str = Field(description="The quiz question text, self-contained and clear.")
    options: List[str] = Field(description="Exactly 4 answer options, in random order.")
    correct_index: int = Field(description="Index (0-3) of the correct option in `options`.")
    explanation: str = Field(description="One short sentence explaining why the correct answer is right.")

    @field_validator("options")
    @classmethod
    def _must_have_four_options(cls, v: List[str]) -> List[str]:
        if len(v) != 4:
            raise ValueError("Each question must have exactly 4 options.")
        return v

    @field_validator("correct_index")
    @classmethod
    def _correct_index_in_range(cls, v: int) -> int:
        if not (0 <= v <= 3):
            raise ValueError("correct_index must be between 0 and 3.")
        return v


class QuizResponse(BaseModel):
    questions: List[QuizQuestion] = Field(description="The full list of generated quiz questions.")


_QUIZ_MODEL_CACHE: dict = {}


def _get_structured_quiz_model(api_key: Optional[str] = None):
    """Create (or reuse) a ChatGroq model bound to the QuizResponse schema."""
    key = api_key or st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    if not key:
        raise ValueError("Groq API key missing from session state and environment variables.")

    if key in _QUIZ_MODEL_CACHE:
        return _QUIZ_MODEL_CACHE[key]

    model_name = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    base_model = ChatGroq(
        model=model_name,
        temperature=0.7,
        max_tokens=2048,
        model_kwargs={"top_p": 0.95},
        api_key=key,
    )
    structured_model = base_model.with_structured_output(QuizResponse)
    _QUIZ_MODEL_CACHE[key] = structured_model
    return structured_model


_QUIZ_PROMPT = ChatPromptTemplate.from_template(
    """You are an expert quiz-writer creating an educational multiple-choice quiz.

Topic: {topic}
Subject area (if relevant): {subject}
Difficulty: {difficulty}
Number of questions: {n}
Generation id (for internal variety only, ignore its value otherwise): {seed}

Rules:
- Write exactly {n} multiple-choice questions strictly about "{topic}", grounded in
  real, accurate, verifiable facts about the topic — no invented facts or incorrect definitions.
- Strictly adhere to standard Artificial Intelligence & Computer Science definitions for acronyms:
  * RAG = Retrieval-Augmented Generation (using vector database retrieval/embeddings to ground LLM responses).
  * CNN = Convolutional Neural Network (computer vision/image processing).
  * RNN = Recurrent Neural Network (sequential data/NLP).
  * LLM = Large Language Model.
  * GAN = Generative Adversarial Network.
  * NLP = Natural Language Processing.
  * SVM = Support Vector Machine.
- Do NOT hallucinate unrelated concepts (e.g., do NOT describe RAG as a Graph Neural Network or project management tool).
- Each question must have exactly 4 options, only ONE of which is correct.
- Distractor (wrong) options must be plausible and topic-relevant (avoid "None of the above" or "Unrelated trivia").
- Match the requested difficulty:
  Easy = recall of basic facts/definitions.
  Medium = applying a concept or comparing ideas.
  Hard = multi-step reasoning, edge cases, or nuanced distinctions.
- Do not repeat the same question twice within this set.
- Keep each question self-contained.
- Provide a clear one-sentence explanation of the correct answer for each question.
{avoid_section}
"""
)


def _fallback_quiz_questions(topic: str, n: int, difficulty: str) -> List[dict]:
    """Used only if the Groq API call fails, so the app never crashes."""
    bank = [
        ("What is the primary purpose of {t}?",
         ["Foundational concept", "Unrelated trivia", "A historical footnote", "None of the above"], 0),
        ("Which of the following best describes a core principle of {t}?",
         ["Randomness only", "Structured, testable logic", "Pure opinion", "Irrelevant data"], 1),
        ("In {t}, which approach is most commonly used to solve core problems?",
         ["Guessing", "Systematic methodology", "Ignoring context", "Avoiding practice"], 1),
        ("A key application of {t} in real life is:",
         ["Everyday problem solving", "Nothing practical", "Only theoretical", "Fictional use only"], 0),
        ("Which statement about {t} is FALSE?",
         ["It has real-world relevance", "It can be studied", "It has no structure or rules", "It is taught in schools"], 2),
        ("What skill is most improved by studying {t}?",
         ["Critical thinking", "Forgetting details", "Avoiding practice", "None"], 0),
    ]
    random.shuffle(bank)
    questions = []
    for i in range(n):
        q, options, correct = bank[i % len(bank)]
        questions.append({
            "question": q.format(t=topic),
            "options": options,
            "correct": correct,
            "difficulty": difficulty,
            "explanation": "Generated offline because the AI quiz service was unavailable.",
        })
    return questions


def generate_quiz(
    topic: str,
    n: int,
    difficulty: str,
    subject: Optional[str] = None,
    avoid: Optional[List[str]] = None,
) -> List[dict]:
    topic = (topic or "").strip()
    if not topic:
        raise ValueError("`topic` must be a non-empty string.")
    n = max(1, min(int(n), 20))
    difficulty = difficulty if difficulty in ("Easy", "Medium", "Hard") else "Medium"

    api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")

    if avoid:
        avoid_list = "\n".join(f"- {q}" for q in avoid[-30:])
        avoid_section = (
            "\nThe learner has already seen the following questions on this topic — "
            f"write a DIFFERENT set that does not repeat or closely rephrase any of these:\n{avoid_list}\n"
        )
    else:
        avoid_section = ""

    if not api_key:
        return _fallback_quiz_questions(topic, n, difficulty)
    
    try:
        model = _get_structured_quiz_model(api_key=api_key)
        chain = _QUIZ_PROMPT | model
        result: QuizResponse = chain.invoke({
            "topic": topic,
            "subject": subject or "General",
            "difficulty": difficulty,
            "n": n,
            "seed": random.randint(100000, 999999),
            "avoid_section": avoid_section,
        })

        out = [
            {
                "question": q.question,
                "options": q.options,
                "correct": q.correct_index,
                "difficulty": difficulty,
                "explanation": q.explanation,
            }
            for q in result.questions[:n]
        ]

        if len(out) < n:
            out += _fallback_quiz_questions(topic, n - len(out), difficulty)

        return out[:n]

    except Exception as exc:  # noqa: BLE001 - any failure falls back safely
        import logging
        logging.getLogger(__name__).warning("Quiz generation via Groq failed, using fallback: %s", exc)
        return _fallback_quiz_questions(topic, n, difficulty)