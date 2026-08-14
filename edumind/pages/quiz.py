import pandas as pd
import streamlit as st

from edumind.generators import generate_quiz
from edumind.personalization import weak_topics
from edumind.storage import add_event
from edumind.ui import page_header


def render_quiz(events: pd.DataFrame) -> None:
    page_header("Quiz Generator", "Questions adapt to your weak topics and every submission updates your progress.")
    weak = weak_topics(events)

    with st.form("quiz_form"):
        topic = st.text_input("Topic", value=weak[0] if weak else "")
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        count = st.slider("Number of questions", 3, 10, 5)
        submitted = st.form_submit_button("Generate quiz", use_container_width=True)

    if submitted and topic:
        st.session_state.quiz = generate_quiz(topic, difficulty, count, weak)
        st.session_state.quiz_topic = topic
        st.session_state.quiz_difficulty = difficulty
        add_event(
            st.session_state.username,
            "quiz_generated",
            topic=topic,
            difficulty=difficulty,
            payload={"count": count, "weak_topics": weak},
        )

    quiz = st.session_state.get("quiz", [])
    if not quiz:
        return

    answers = {}
    for idx, q in enumerate(quiz):
        st.markdown(f"<div class='question-box'><b>{idx + 1}. {q['question']}</b></div>", unsafe_allow_html=True)
        answers[idx] = st.radio(
            "Choose one",
            q["options"],
            index=None,  # Prevents auto-selecting the first option
            key=f"quiz_answer_{idx}",
            label_visibility="collapsed",
        )

    if st.button("Submit quiz", use_container_width=True):
        # Calculate score safely when questions are left unanswered (answers[i] is None)
        score = sum(
            1 for i, q in enumerate(quiz)
            if answers[i] is not None and q["options"].index(answers[i]) == int(q["correct"])
        )
        add_event(
            st.session_state.username,
            "quiz_submitted",
            topic=st.session_state.quiz_topic,
            score=score,
            total=len(quiz),
            difficulty=st.session_state.quiz_difficulty,
            payload={"questions": quiz},
        )
        st.success(f"Score: {score}/{len(quiz)}")
        for i, q in enumerate(quiz):
            st.info(f"{i + 1}. {q.get('explanation', 'Review this concept before the next attempt.')}")