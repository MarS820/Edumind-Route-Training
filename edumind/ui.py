import streamlit as st

from edumind.config import FEATURES
from edumind.storage import create_or_login
from edumind.styles import apply_styles

apply_styles()

def login_screen() -> None:
    st.markdown("""<div class="login-container">
<div class="login-card">
<div class="brand-title">🧠 EduMind AI</div>
<div class="brand-sub">
Personalized learning powered by AI
</div>
</div>
</div>
    """, unsafe_allow_html=True)

    _, center, _ = st.columns([1, 1.15, 1])

    with center:
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        groq_api_key = st.text_input(
            "Groq API Key",
            type="password",
            help="Get a free key at console.groq.com/keys. Used for quizzes, assignments, and chat.",
)
        if st.button("Continue", use_container_width=True):
            if not groq_api_key.strip():
                st.error("A Groq API key is required to continue.")
                return
            ok, message = create_or_login(username, password)

            if ok:
                st.session_state.authenticated = True
                st.session_state.username = username.strip().lower()
                st.session_state.groq_api_key = groq_api_key.strip()
                st.success(message)
                st.rerun()

            st.error(message)

def render_sidebar() -> None:
    with st.sidebar:

        st.markdown("""<div class="brand-title">
🧠 EduMind AI
</div>

<div class="brand-sub">
PERSONAL LEARNING ASSISTANT
</div>
        """, unsafe_allow_html=True)

        st.markdown("---", unsafe_allow_html=True)

        st.markdown(f"""
<div class="glass-card">
<h4>👤 {st.session_state.username.title()}</h4>
<p class="muted">
Ready to learn today
</p>
</div>
        """, unsafe_allow_html=True)

        st.markdown("### Navigation", unsafe_allow_html=True)

        icons = {
            "Overview": "🏠",
            "Student Progress Dashboard": "📊",
            "Quiz Generator": "📝",
            "Flashcards": "🗂️",
            "Assignment Generator": "📄",
            "Chat with Lecture PDFs": "💬",
            "Personalized Learning": "🧠",
        }

        for item in FEATURES:

            label = f"{icons.get(item,'📌')} {item}"

            if st.button(label, key=f"nav_{item}", use_container_width=True):
                st.session_state.page = item
                st.rerun()

        st.markdown("---", unsafe_allow_html=True)

        if st.button("🚪 Log Out", use_container_width=True):
            st.session_state.clear()
            st.rerun()

def page_header(title: str, subtitle: str, icon: str = "🧠") -> None:
    st.markdown(
        f"""<div class="hero-panel">
<div style="display:flex;align-items:center;gap:18px;">
<div style="width:60px;height:60px;border-radius:18px;background:#6C5CE7;display:flex;justify-content:center;align-items:center;font-size:30px;">{icon}</div>
<div>
<h1 style="margin-bottom:4px;">{title}</h1>
<p class="muted">{subtitle}</p>
</div>
</div>
</div>""",
        unsafe_allow_html=True,
    )