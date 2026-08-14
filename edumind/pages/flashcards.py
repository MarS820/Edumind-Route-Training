import pandas as pd
import streamlit as st

from edumind.generators import generate_flashcards
from edumind.personalization import weak_topics
from edumind.storage import add_event
from edumind.ui import page_header


def render_flashcards(events: pd.DataFrame) -> None:
    page_header("Flashcards", "Generate focused review cards from your current learning patterns.")
    weak = weak_topics(events)
    col1, col2 = st.columns([2, 1])
    topic = col1.text_input("Topic", value=weak[0] if weak else "")
    count = col2.slider("Cards", 3, 12, 6)

    if st.button("Generate flashcards", use_container_width=True) and topic:
        st.session_state.flashcards = generate_flashcards(topic, count, weak)
        st.session_state.flash_index = 0
        st.session_state.flash_show_back = False
        add_event(st.session_state.username, "flashcards_generated", topic=topic, payload={"count": count, "weak_topics": weak})

    cards = st.session_state.get("flashcards", [])
    if not cards:
        return

    idx = st.session_state.get("flash_index", 0)
    card = cards[idx]
    st.progress((idx + 1) / len(cards))
    
    flipped_class = "is-flipped" if st.session_state.get("flash_show_back") else ""
    st.markdown(
        f"""<div class="flip-card">
<div class="flip-card-inner {flipped_class}">
<div class="flip-card-face flip-card-front">
<div>
<div class="flash-tag">Front</div>
<div class="flip-card-content">{card["front"]}</div>
</div>
</div>
<div class="flip-card-face flip-card-back">
<div>
<div class="flash-tag">Back</div>
<div class="flip-card-content">{card["back"]}</div>
</div>
</div>
</div>
</div>
        """,
        unsafe_allow_html=True,
    )
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Previous", use_container_width=True, disabled=idx == 0):
        st.session_state.flash_index -= 1
        st.session_state.flash_show_back = False
        st.rerun()
    if c2.button("Flip", use_container_width=True):
        st.session_state.flash_show_back = not st.session_state.get("flash_show_back")
        add_event(st.session_state.username, "flashcard_reviewed", topic=topic, payload={"index": idx})
        st.rerun()
    if c3.button("Next", use_container_width=True, disabled=idx >= len(cards) - 1):
        st.session_state.flash_index += 1
        st.session_state.flash_show_back = False
        st.rerun()
