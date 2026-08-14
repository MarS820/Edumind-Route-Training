import pandas as pd
import streamlit as st

from edumind.generators import generate_assignment
from edumind.personalization import weak_topics
from edumind.storage import add_event
from edumind.ui import page_header


def render_assignment(events: pd.DataFrame) -> None:
    page_header("Assignment Generator", "Create practice work from a topic, lecture notes, or pasted course material.")
    weak = weak_topics(events)

    with st.form("assignment_form"):
        topic = st.text_input("Topic", value=weak[0] if weak else "")
        source = st.text_area("Source material or lecture notes", height=160)
        student_level = st.text_input("Student level", value="Beginner university students")
        assignment_type = st.selectbox("Assignment type", ["Mixed questions", "Short answer", "Case study", "Problem set"])
        difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"], index=1)
        count = st.slider("Number of questions", 3, 12, 5)
        submitted = st.form_submit_button("Generate assignment", use_container_width=True)

    if submitted and topic:
        result = generate_assignment(topic, source or topic, student_level, assignment_type, difficulty, count)
        st.session_state.assignment_text = result
        add_event(st.session_state.username, "assignment_generated", topic=topic, difficulty=difficulty, payload={"type": assignment_type, "count": count})

    if st.session_state.get("assignment_text"):
        st.markdown(st.session_state.assignment_text)
        st.download_button("Download assignment", st.session_state.assignment_text, file_name="assignment.md", use_container_width=True)
