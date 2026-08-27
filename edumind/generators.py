import json
import os
from functools import lru_cache
from typing import Any, Literal, TypedDict

from groq import Groq
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph
from pydantic import BaseModel, Field
import streamlit as st

from edumind.ai import call_ai, extract_json_list
from quiz_generator import generate_quiz as generate_quiz_from_file


def generate_quiz(topic: str, difficulty: str, count: int, weak_topics: list[str]) -> list[dict[str, Any]]:
    subject = ", ".join(weak_topics) if weak_topics else None
    return generate_quiz_from_file(topic=topic, n=count, difficulty=difficulty, subject=subject)

'''
def get_groq_client() -> Groq:
    api_key = st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY")
    return Groq(api_key=api_key)


def generate_flashcards(topic: str, n: int, weak_topics: list[str] | None = None) -> list[dict[str, Any]]:
    client = get_groq_client()

    focus_note = ""
    if weak_topics:
        focus_note = f"\nPay extra attention to these weak areas: {', '.join(weak_topics)}."

    prompt = f"""Generate exactly {n} flashcards for the topic: '{topic}'.{focus_note}

CRITICAL DOMAIN & ACRONYM RULE:
- You are strictly an AI and Computer Science tutoring platform.
- If the topic is an isolated acronym or ambiguous keyword (e.g., 'RAG', 'CNN', 'ANN', 'NLP', 'LLM', 'SVM'), 
  ALWAYS default strictly to its Artificial Intelligence / Machine Learning / Computer Science definition 
  (e.g., 'RAG' MUST be expanded as 'Retrieval-Augmented Generation', NOT project management terms like 'Red, Amber, Green').
- Do NOT use business, finance, or general project management jargon unless explicitly instructed.

Return a JSON object with this exact shape:
{{"cards": [{{"front": "...", "back": "..."}}, ...]}}
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Computer Science and AI tutor for a "
                        "programming education platform. Always interpret topics "
                        "strictly within a software engineering / AI / CS context. "
                        "Respond only with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
            max_tokens=2000,
        )

        raw_text = response.choices[0].message.content or "{}"
        data = json.loads(raw_text)
        cards = data.get("cards", [])

        valid_cards = [
            c for c in cards
            if isinstance(c, dict) and "front" in c and "back" in c
        ]

        if not valid_cards:
            raise ValueError("No valid cards returned")

        return valid_cards[:n]

    except Exception as e:
        return [
            {
                "front": "Error Generating Cards",
                "back": f"Could not connect to Groq API. Error: {str(e)}",
            }
        ]
'''

def get_groq_client():
    return Groq(api_key=st.session_state.get("groq_api_key"))


def generate_flashcards(topic: str, n: int, weak_topics: list[str] | None = None) -> list:
    client = get_groq_client()

    focus_note = ""
    if weak_topics:
        focus_note = f"\nPay extra attention to these weak areas: {', '.join(weak_topics)}."

    prompt = f"""Generate exactly {n} flashcards for the topic: '{topic}'.{focus_note}

If the topic contains an acronym or ambiguous term, resolve it using the
most relevant technical/academic meaning in the context of the given topic
wording (e.g. if the topic mentions "programming", "AI", "software", or
"machine learning", prefer the computer-science meaning over unrelated
industry jargon).

Return a JSON object with this exact shape:
{{"cards": [{{"front": "...", "back": "..."}}, ...]}}
"""

    try:
        response = client.chat.completions.create(
            model="qwen/qwen3.6-27b",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an expert Computer Science and AI tutor for a "
                        "programming education platform. Always interpret topics "
                        "in a software engineering / AI / CS context unless "
                        "explicitly stated otherwise. Respond only with valid JSON."
                    ),
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        ...

        raw_text = response.choices[0].message.content
        data = json.loads(raw_text)
        cards = data.get("cards", [])

        # تحقق من صحة كل بطاقة
        valid_cards = [
            c for c in cards
            if isinstance(c, dict) and "front" in c and "back" in c
        ]

        if not valid_cards:
            raise ValueError("No valid cards returned")

        return valid_cards[:n]

    except Exception as e:
        return [
            {
                "front": "Error Generating Cards",
                "back": f"Could not connect to Groq API. Error: {str(e)}",
            }
        ]

# =====================================================
# Assignment Generator
# =====================================================

class AssignmentState(TypedDict):
    topic: str
    source_data: str
    student_level: str
    assignment_type: str
    difficulty: str
    number_of_questions: int

    draft_assignment: str
    review_feedback: str
    approved: bool
    final_assignment: str


class ReviewResult(BaseModel):
    approved: bool = Field(
        description="True only when the assignment satisfies all requested requirements."
    )
    feedback: str = Field(
        description="Short and specific corrections or approval message."
    )


@lru_cache(maxsize=8)
def build_assignment_graph(
    model_name: str = "qwen/qwen3.6-27b",
    api_key: str | None = None,
):
    model = ChatGroq(
        api_key=api_key or st.session_state.get("groq_api_key") or os.getenv("GROQ_API_KEY"),
        model=model_name,
        temperature=0.2,
        timeout=60,
        max_retries=2,
    )

    reviewer_model = model.with_structured_output(ReviewResult)

    def generate_node(state: AssignmentState):
        response = model.invoke([
            SystemMessage(
                content="""
You are a professional educational assignment designer.

Create an assignment using only the supplied source material.

Do not use outside information.
Do not provide answers or solutions.
Return only the assignment.
"""
            ),
            HumanMessage(
                content=f"""
TOPIC:
{state['topic']}

SOURCE MATERIAL:
{state['source_data']}

STUDENT LEVEL:
{state['student_level']}

ASSIGNMENT TYPE:
{state['assignment_type']}

DIFFICULTY:
{state['difficulty']}

NUMBER OF QUESTIONS:
{state['number_of_questions']}

Create an assignment containing:

- Assignment title
- Learning objectives
- Clear student instructions
- Exactly {state['number_of_questions']} numbered questions
- Marks for every question
- Total marks
- A short grading rubric

Rules:

- Use only the supplied source material.
- Make questions suitable for the requested level.
- Follow the requested assignment type.
- Do not include answers or solutions.
- Return only the assignment.
"""
            ),
        ])

        return {
            "draft_assignment": str(response.content).strip(),
            "review_feedback": "",
            "approved": False,
            "final_assignment": "",
        }

    def review_node(state: AssignmentState):
        review = reviewer_model.invoke([
            SystemMessage(
                content="""
You are a strict educational assignment reviewer.

Approve only when every requirement is satisfied.

Check that every question is supported by the supplied
source material.
"""
            ),
            HumanMessage(
                content=f"""
SOURCE MATERIAL:

{state['source_data']}

ASSIGNMENT:

{state['draft_assignment']}

Check that:

1. The topic is: {state['topic']}
2. The student level is: {state['student_level']}
3. The assignment type is: {state['assignment_type']}
4. The difficulty is: {state['difficulty']}
5. There are exactly {state['number_of_questions']} questions
6. Every question has marks
7. Total marks are included
8. Instructions are clear
9. A grading rubric is included
10. No answers or solutions are included
11. All questions are supported by the source
12. No outside information is used
"""
            ),
        ])

        return {
            "approved": review.approved,
            "review_feedback": review.feedback.strip(),
            "final_assignment": (
                state["draft_assignment"]
                if review.approved
                else ""
            ),
        }

    def improve_node(state: AssignmentState):
        response = model.invoke([
            SystemMessage(
                content="""
Correct the assignment using the reviewer feedback.

Use only the supplied source material.

Return only the corrected assignment.
"""
            ),
            HumanMessage(
                content=f"""
SOURCE MATERIAL:

{state['source_data']}

ORIGINAL ASSIGNMENT:

{state['draft_assignment']}

REVIEWER FEEDBACK:

{state['review_feedback']}
"""
            ),
        ])

        return {
            "final_assignment": str(response.content).strip()
        }

    def route_after_review(state: AssignmentState) -> Literal["finish", "improve"]:
        if state["approved"]:
            return "finish"
        return "improve"

    graph_builder = StateGraph(AssignmentState)

    graph_builder.add_node("generate", generate_node)
    graph_builder.add_node("review", review_node)
    graph_builder.add_node("improve", improve_node)

    graph_builder.add_edge(START, "generate")
    graph_builder.add_edge("generate", "review")
    graph_builder.add_conditional_edges(
        "review",
        route_after_review,
        {
            "finish": END,
            "improve": "improve",
        },
    )
    graph_builder.add_edge("improve", END)

    return graph_builder.compile()


def generate_assignment(
    topic: str,
    source: str,
    student_level: str,
    assignment_type: str,
    difficulty: str,
    count: int,
) -> str:

    graph = build_assignment_graph(api_key=st.session_state.get("groq_api_key"))

    result = graph.invoke({
        "topic": topic,
        "source_data": source,
        "student_level": student_level,
        "assignment_type": assignment_type,
        "difficulty": difficulty.title(),
        "number_of_questions": count,
        "draft_assignment": "",
        "review_feedback": "",
        "approved": False,
        "final_assignment": "",
    })

    return (
        result.get("final_assignment")
        or result.get("draft_assignment")
        or ""
    ).strip()
