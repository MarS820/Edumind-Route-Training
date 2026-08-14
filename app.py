import streamlit as st

from edumind.pages.assignment import render_assignment
from edumind.pages.dashboard import render_dashboard
from edumind.pages.flashcards import render_flashcards
from edumind.pages.overview import render_overview
from edumind.pages.pdf_chat import render_pdf_chat
from edumind.pages.personalized import render_personalized_learning
from edumind.pages.quiz import render_quiz
from edumind.storage import get_events
from edumind.styles import apply_styles
from edumind.ui import login_screen, render_sidebar


st.set_page_config(
    page_title="EduMind AI",
    page_icon=":mortar_board:",
    layout="wide",
    initial_sidebar_state="expanded",
)
apply_styles()

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Overview"

if not st.session_state.authenticated:
    login_screen()
    st.stop()

render_sidebar()
events_df = get_events(st.session_state.username)
page = st.session_state.page

if page == "Overview":
    render_overview(events_df)
elif page == "Quiz Generator":
    render_quiz(events_df)
elif page == "Flashcards":
    render_flashcards(events_df)
elif page == "Assignment Generator":
    render_assignment(events_df)
elif page == "Chat with Lecture PDFs":
    render_pdf_chat()
elif page == "Student Progress Dashboard":
    render_dashboard(events_df)
elif page == "Personalized Learning":
    render_personalized_learning(events_df)