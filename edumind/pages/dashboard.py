from datetime import datetime

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from edumind.personalization import weak_topics
from edumind.ui import page_header


def render_dashboard(events: pd.DataFrame) -> None:
    page_header("Student Progress Dashboard", "Live charts from your saved activity.")

    if events.empty:
        st.info("No activity yet. Generate a quiz, flashcard deck, assignment, or PDF chat to populate the dashboard.")
        return

    quiz = events[events["event_type"] == "quiz_submitted"].copy()
    if not quiz.empty:
        quiz["score_percent"] = (quiz["score"] / quiz["total"].replace(0, 1)) * 100

    now = datetime.now()

    # -----------------------------
    # Metric Cards
    # -----------------------------
    if not quiz.empty:
        overall_mastery = round(quiz["score_percent"].mean())
        mastery_display = f"{overall_mastery}%"
        if len(quiz) > 1:
            quiz_sorted = quiz.sort_values("created_at")
            first_score = quiz_sorted["score_percent"].iloc[0]
            last_score = quiz_sorted["score_percent"].iloc[-1]
            diff = round(last_score - first_score)
            mastery_delta = f"{'+' if diff >= 0 else ''}{diff}% vs first attempt"
        else:
            mastery_delta = "First attempt logged"
    else:
        mastery_display = "—"
        mastery_delta = "No quizzes yet"

    quizzes_this_month = int(
        (
            (quiz["created_at"].dt.month == now.month) & (quiz["created_at"].dt.year == now.year)
        ).sum()
    ) if not quiz.empty else 0
    quizzes_delta = f"{len(quiz)} total attempts" if not quiz.empty else "Take a quiz to begin"

    assignment_count = int((events["event_type"] == "assignment_generated").sum())
    assignments_delta = "Generated so far" if assignment_count else "None generated yet"

    weak_count = len(weak_topics(events))

    m1, m2, m3, m4 = st.columns(4)
    dash_metrics = [
        ("Overall Mastery", mastery_display, mastery_delta),
        ("Quizzes This Month", str(quizzes_this_month), quizzes_delta),
        ("Assignments Generated", str(assignment_count), assignments_delta),
        ("Weak Topics", str(weak_count), "Need more practice"),
    ]
    for col, (label, value, delta) in zip([m1, m2, m3, m4], dash_metrics):
        with col:
            st.markdown(
                f"""<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{value}</div><div class="metric-delta-up">{delta}</div></div>""",
                unsafe_allow_html=True,
            )

    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)

    # -----------------------------
    # Activity over time
    # -----------------------------
    events_by_day = events.copy()
    events_by_day["day"] = events_by_day["created_at"].dt.date
    daily = events_by_day.groupby(["day", "event_type"]).size().reset_index(name="count")
    st.plotly_chart(
        px.bar(daily, x="day", y="count", color="event_type", title="Activity over time"),
        use_container_width=True,
    )

    # -----------------------------
    # Quiz performance + Mastery by topic
    # -----------------------------
    if not quiz.empty:
        g1, g2 = st.columns([2, 1])

        with g1:
            st.plotly_chart(
                px.line(
                    quiz.sort_values("created_at"),
                    x="created_at",
                    y="score_percent",
                    color="topic",
                    title="Quiz performance",
                ),
                use_container_width=True,
            )

        with g2:
            st.markdown("##### Mastery by Topic")
            topic_avg = (
                quiz.groupby("topic")["score_percent"]
                .mean()
                .round()
                .reset_index()
                .sort_values("score_percent", ascending=True)
            )
            fig2 = go.Figure(
                go.Bar(
                    x=topic_avg["score_percent"],
                    y=topic_avg["topic"],
                    orientation="h",
                    marker_color="#6C5CE7",
                )
            )
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font_color="#F1F5F9",
                margin=dict(l=10, r=10, t=10, b=10),
                xaxis=dict(range=[0, 100], gridcolor="rgba(148,163,184,0.1)"),
            )
            st.plotly_chart(fig2, use_container_width=True)

        st.dataframe(
            quiz[["created_at", "topic", "difficulty", "score", "total", "score_percent"]],
            use_container_width=True,
        )
    else:
        st.info("Take a quiz to see performance charts here.")

    # -----------------------------
    # Recent Activity
    # -----------------------------
    st.markdown("<div class='divider-line'></div>", unsafe_allow_html=True)
    st.markdown("##### Recent Activity")

    def describe_event(row: pd.Series) -> tuple[str, str]:
        event_type = row["event_type"]
        topic = row.get("topic") or "—"

        if event_type == "quiz_submitted":
            score = row.get("score")
            total = row.get("total")
            pct = round((score / total) * 100) if total else 0
            return f"Quiz: {topic}", f"{pct}% ({score}/{total})"
        if event_type == "assignment_generated":
            return f"Assignment: {topic}", "Generated"
        if event_type == "pdf_uploaded":
            return f"PDF Uploaded: {topic}", "Ready"
        import json

        if event_type == "pdf_question":
            payload = row.get("payload")
            if isinstance(payload, str):
                try:
                    payload = json.loads(payload)
                except json.JSONDecodeError:
                    payload = {}
            question = payload.get("question", "") if isinstance(payload, dict) else ""
            return f"PDF Chat: {topic}", (question[:40] + "…") if len(question) > 40 else question
        return event_type.replace("_", " ").title(), topic

    recent = events.sort_values("created_at", ascending=False).head(10).copy()
    rows = []
    for _, row in recent.iterrows():
        activity, status = describe_event(row)
        rows.append(
            {
                "Date": row["created_at"].strftime("%b %d, %H:%M"),
                "Activity": activity,
                "Score / Status": status,
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)