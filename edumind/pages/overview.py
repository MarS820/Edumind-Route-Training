import pandas as pd
import streamlit as st

from edumind.personalization import recommendation_plan, weak_topics
from edumind.ui import page_header
from edumind.styles import apply_styles

apply_styles()

def render_overview(events: pd.DataFrame) -> None:
    page_header(
        "Learning Overview",
        "Your workspace connects quizzes, flashcards, assignments, PDFs, progress, and recommendations."
    )

    # -----------------------------
    # Dynamic Metrics
    # -----------------------------
    total_events = len(events)

    quiz_events = events[events["event_type"] == "quiz_submitted"]

    avg_score = (
        0
        if quiz_events.empty
        else round((quiz_events["score"].sum() / quiz_events["total"].sum()) * 100)
    )

    active_topics = (
        events["topic"].dropna().nunique()
        if not events.empty
        else 0
    )

    weak_count = len(weak_topics(events))


    # -----------------------------
    # Overview Metric Cards
    # -----------------------------
    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        (
            "Activities",
            str(total_events),
            "Learning interactions",
            "📚",
            "rgba(255,176,32,0.15)"
        ),
        (
            "Average Quiz Score",
            f"{avg_score}%",
            "Overall performance",
            "🎯",
            "rgba(0,217,192,0.15)"
        ),
        (
            "Topics Studied",
            str(active_topics),
            "Subjects explored",
            "📝",
            "rgba(108,92,231,0.18)"
        ),
        (
            "Weak Topics",
            str(weak_count),
            "Need more practice",
            "⚠️",
            "rgba(251,113,133,0.15)"
        ),
    ]


    for col, (label, value, delta, icon, bg) in zip(
        [c1, c2, c3, c4],
        metrics
    ):
        with col:
            st.markdown(
                f"""<div class="metric-card">

<div class="metric-icon" 
style="background:{bg};">
{icon}
</div>

<div class="metric-label">
{label}
</div>

<div class="metric-value">
{value}
</div>

<div class="metric-delta-up">
{delta}
</div>

</div>
""",
unsafe_allow_html=True,
            )


    st.markdown("<div class='divider-line'></div>",
        unsafe_allow_html=True
    )


    # -----------------------------
    # Feature Cards
    # -----------------------------
    st.markdown("### Explore Platform Features", unsafe_allow_html=True)


    feature_cards = [
        (
            "📝",
            "Quiz Generator",
            "Generate personalized quizzes based on your learning history."
        ),
        (
            "🗂️",
            "Flashcards",
            "Create active recall flashcards for faster revision."
        ),
        (
            "📋",
            "Assignment Generator",
            "Generate structured assignments and practice tasks."
        ),
        (
            "💬",
            "Chat with Lecture PDFs",
            "Ask questions and summarize uploaded learning materials."
        ),
        (
            "📊",
            "Progress Dashboard",
            "Track your scores, activities, and mastery progress."
        ),
        (
            "🧭",
            "Personalized Learning",
            "Receive adaptive recommendations based on weaknesses."
        ),
    ]


    cols = st.columns(3)

    for i, (icon, title, desc) in enumerate(feature_cards):

        with cols[i % 3]:

            st.markdown(
                f"""<div class="card" 
style="min-height:150px; margin-bottom:1rem;">

<div style="font-size:1.6rem;">
{icon}
</div>

<div style="
font-weight:700;
margin-top:0.4rem;">
{title}
</div>

<div style="
color:#94A3B8;
font-size:0.85rem;
margin-top:0.3rem;">
{desc}
</div>

</div>
""",
                unsafe_allow_html=True,
            )

'''
    # -----------------------------
    # Recommendations Section
    # -----------------------------
    st.markdown(
        "<div class='divider-line'></div>",
        unsafe_allow_html=True
    )

    st.markdown("### Recommended Next Steps")


    recommendations = recommendation_plan(events)

    if recommendations:
        for step in recommendations:
            st.markdown(
                f"""<div class="card" 
style="margin-bottom:0.8rem;">
{step}
</div>
""",
                unsafe_allow_html=True,
            )
    else:
        st.info("Complete more activities to generate personalized recommendations.")
'''