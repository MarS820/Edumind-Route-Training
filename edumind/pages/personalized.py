import pandas as pd
import streamlit as st

from edumind.generators import generate_quiz
from edumind.personalization import (
    recommendation_plan, 
    strong_topics, 
    weak_topics, 
    get_learning_insights, 
    get_learning_pace
)
from edumind.storage import add_event
from edumind.ui import page_header


# ============================
# LOCAL UI HELPER FUNCTIONS
# ============================

def hero_section(content: str, icon: str = "✨") -> None:
    """Create a hero/featured section using existing CSS"""
    st.markdown(f"""<div class="hero-panel">
<div style="display: flex; align-items: center; gap: 0.8rem; margin-bottom: 0.5rem;">
<span style="font-size: 2rem;">{icon}</span>
<div style="font-size: 1.1rem; font-weight: 500;">{content}</div>
</div>
</div>
    """, unsafe_allow_html=True)


def render_metric_row(metrics: list[dict]) -> None:
    """Render a row of metric cards using existing CSS"""
    cols = st.columns(len(metrics))
    for col, metric in zip(cols, metrics):
        with col:
            st.markdown(f"""<div class="metric-card">
<div style="display: flex; align-items: center; gap: 0.6rem;">
<span style="font-size: 1.2rem;">{metric.get('icon', '')}</span>
<div class="metric-label">{metric['label']}</div>
</div>
<div class="metric-value">{metric['value']}</div>
</div>
            """, unsafe_allow_html=True)


def pill(text: str, type: str = "medium") -> str:
    """Generate a pill badge HTML using existing CSS classes"""
    return f'<span class="pill pill-{type}">{text}</span>'


def render_personalized_learning(events: pd.DataFrame) -> None:
    """Render personalized learning page with insights and recommendations"""
    
    # Page header using existing ui.py function
    page_header(
        "Personalized Learning", 
        "Your learning insights and adaptive recommendations based on your activity",
        icon="🎯"
    )
    
    # Empty state handling
    if events.empty:
        hero_section(
            "📚 Start learning to unlock personalized insights! Upload PDFs, take quizzes, and generate assignments.",
            icon="🚀"
        )
        return
    
    # Get insights using your personalization functions
    weak = weak_topics(events)
    strong = strong_topics(events)
    recommendations = recommendation_plan(events)
    insights = get_learning_insights(events)
    pace = get_learning_pace(events)
    
    # --- LEARNING PACE SECTION ---
    pace_icon = {
        "accelerating": "🚀",
        "steady": "⚖️", 
        "slowing": "🐢",
        "sporadic": "📉",
        "starting": "🌟"
    }.get(pace.get("pace", "steady"), "📊")
    
    pace_text = {
        "accelerating": "You're accelerating! Keep up the momentum!",
        "steady": "Steady progress! You're building strong habits.",
        "slowing": "Take a breather and review your notes.",
        "sporadic": "Try to be more consistent with daily practice.",
        "starting": "Great start! Build momentum with daily practice."
    }.get(pace.get("pace", "steady"), "Keep going!")
    
    hero_section(
        f"{pace_icon} {pace_text} • {len(events)} total activities tracked", 
        icon=pace_icon
    )
    
    # --- METRICS ROW ---
    metric_items = [
        {"label": "Weak Topics", "value": str(len(weak)), "icon": "🔴"},
        {"label": "Strong Topics", "value": str(len(strong)), "icon": "💪"},
        {"label": "Total Activities", "value": str(len(events)), "icon": "📊"},
    ]
    render_metric_row(metric_items)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- TOPICS SECTION (Two Columns) ---
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### 🔴 Weak Topics")
        if weak:
            weak_tags = " ".join(pill(topic, "hard") for topic in weak)
            st.markdown(f"<div style='margin-bottom: 0.5rem;'>{weak_tags}</div>", unsafe_allow_html=True)
            st.caption("Focus on these topics to improve")
        else:
            st.info("✅ No weak topics detected! Great job!")
    
    with col2:
        st.markdown("##### 💪 Strong Topics")
        if strong:
            strong_tags = " ".join(pill(topic, "easy") for topic in strong)
            st.markdown(f"<div style='margin-bottom: 0.5rem;'>{strong_tags}</div>", unsafe_allow_html=True)
            st.caption("You're excelling in these areas")
        else:
            st.info("📝 Build more quiz history to detect strengths")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # --- RECOMMENDATIONS WITH ACTION BUTTONS ---
    st.markdown("""
    <div class="glass-card" style="margin-bottom: 1rem;">
        <h3 style="margin-top: 0; margin-bottom: 0.8rem; font-size: 1.1rem;">📋 Your Adaptive Learning Plan</h3>
    """, unsafe_allow_html=True)
    
    if recommendations:
        for i, rec in enumerate(recommendations, 1):
            # Extract action type from recommendation text
            rec_lower = rec.lower()
            
            # Determine action type and button label
            if "flashcard" in rec_lower or "flashcards" in rec_lower:
                action_type = "Flashcards"
                button_label = "🗂️ Go to Flashcards"
            elif "quiz" in rec_lower or "quiz" in rec_lower:
                action_type = "Quiz Generator"
                button_label = "📝 Go to Quiz Generator"
            elif "assignment" in rec_lower or "practice" in rec_lower:
                action_type = "Assignment Generator"
                button_label = "📄 Go to Assignment Generator"
            elif "pdf" in rec_lower or "lecture" in rec_lower:
                action_type = "Chat with Lecture PDFs"
                button_label = "💬 Go to PDF Chat"
            else:
                action_type = None
                button_label = None
            
            # Display recommendation with action button
            col_rec, col_btn = st.columns([4, 1.5])
            
            with col_rec:
                st.markdown(f"""
                <div style="display: flex; align-items: flex-start; gap: 0.8rem; padding: 0.6rem 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                    <div style="background: linear-gradient(135deg, #6C5CE7, #00D9C0); width: 24px; height: 24px; min-width: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7rem; font-weight: 700; color: white;">{i}</div>
                    <div>{rec}</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col_btn:
                if action_type and button_label:
                    if st.button(button_label, key=f"action_btn_{i}", use_container_width=True):
                        st.session_state.page = action_type
                        st.rerun()
                else:
                    # Show a small icon if no specific action
                    st.markdown("<div style='text-align: center; padding: 0.5rem 0;'>✨</div>", unsafe_allow_html=True)
        
        # Special: Generate Recovery Quiz button if weak topics exist
        if weak:
            st.markdown("<div style='margin-top: 0.8rem;'></div>", unsafe_allow_html=True)
            if st.button(f"📝 Generate Recovery Quiz: {weak[0]}", use_container_width=True, type="primary"):
                st.session_state.page = "Quiz Generator"
                st.session_state.quiz = generate_quiz(weak[0], "Medium", 5, weak)
                st.session_state.quiz_topic = weak[0]
                st.session_state.quiz_difficulty = "Medium"
                add_event(
                    st.session_state.username, 
                    "personalized_quiz_generated", 
                    topic=weak[0], 
                    difficulty="Medium", 
                    payload={"weak_topics": weak}
                )
                st.rerun()
            
            if len(weak) > 1:
                st.caption(f"📌 Other weak topics: {', '.join(weak[1:])}")
    else:
        st.info("No recommendations yet. Keep learning!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- DETAILED STATS (Expandable) ---
    with st.expander("📊 Detailed Activity Stats", expanded=False):
        # Activity breakdown
        event_counts = events["event_type"].value_counts()
        
        st.write("**Activity Breakdown**")
        
        col1, col2, col3, col4 = st.columns(4)
        
        event_map = {
            "quiz_submitted": ("📝", "Quizzes"),
            "pdf_question": ("📄", "PDF Questions"), 
            "assignment_generated": ("✍️", "Assignments"),
            "pdf_uploaded": ("📚", "PDFs Uploaded")
        }
        
        cols = [col1, col2, col3, col4]
        for i, (event_type, (icon, label)) in enumerate(event_map.items()):
            if i < len(cols):
                with cols[i]:
                    count = event_counts.get(event_type, 0)
                    st.metric(label, count)
        
        st.markdown("---")
        
        # Topic distribution
        if "topic" in events.columns:
            topic_counts = events[events["topic"].notna()]["topic"].value_counts()
            if not topic_counts.empty:
                st.write("**📚 Topic Distribution**")
                st.dataframe(
                    topic_counts.reset_index().rename(
                        columns={"index": "Topic", "topic": "Activity Count"}
                    ),
                    use_container_width=True,
                    hide_index=True
                )
        
        # Recent activity
        if "timestamp" in events.columns:
            st.write("**📅 Recent Activity**")
            recent = events.sort_values("timestamp", ascending=False).head(5)
            
            display_cols = ["event_type", "topic", "timestamp"]
            if all(col in recent.columns for col in display_cols):
                recent_display = recent[display_cols].copy()
                recent_display["timestamp"] = recent_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
                recent_display = recent_display.rename(columns={
                    "event_type": "Event",
                    "topic": "Topic",
                    "timestamp": "Time"
                })
                st.dataframe(recent_display, use_container_width=True, hide_index=True)
    
    # --- FOOTER ---
    st.markdown("---")
    st.caption("💡 Your learning data helps personalize recommendations. Keep exploring and learning!")