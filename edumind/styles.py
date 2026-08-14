import streamlit as st


CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Sora:wght@600;700;800&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }

    :root {
        --bg-primary: #0B0F19;
        --bg-secondary: #111827;
        --bg-card: #161C2C;
        --accent: #6C5CE7;
        --accent-2: #00D9C0;
        --accent-warm: #FFB020;
        --text-primary: #F1F5F9;
        --text-secondary: #94A3B8;
        --border-color: rgba(148, 163, 184, 0.12);
    }
    
    .main-container{
        max-width:1200px;
        margin:auto;
        padding-top:1rem;
        padding-bottom:2rem;
    }

    .stApp {
        position: relative;
        background: #0B0F19;
        color: var(--text-primary);
        overflow-x: hidden;
    }

    .stApp::before,
    .stApp::after {
        content: "";
        position: fixed;
        border-radius: 42% 58% 65% 35% / 45% 40% 60% 55%;
        filter: blur(70px);
        z-index: 0;
        pointer-events: none;
        animation: morphBlob 16s ease-in-out infinite, floatBlob 20s ease-in-out infinite;
    }

    .stApp::before {
        width: 480px;
        height: 480px;
        background: var(--accent);
        opacity: 0.22;
        top: -120px;
        left: -120px;
    }

    .stApp::after {
        width: 420px;
        height: 420px;
        background: var(--accent-2);
        opacity: 0.18;
        bottom: -120px;
        right: -100px;
        animation-delay: -8s, -4s;
    }
    
    [data-testid="stAppViewContainer"] {
        position: relative;
        z-index: 1;
    }

    @keyframes morphBlob {
        0%, 100% { border-radius: 42% 58% 65% 35% / 45% 40% 60% 55%; }
        50% { border-radius: 65% 35% 40% 60% / 55% 65% 35% 45%; }
    }

    @keyframes floatBlob {
        0%, 100% { transform: translate(0, 0) scale(1); }
        50% { transform: translate(60px, 40px) scale(1.1); }
    }

    /* --- LOGIN SPECIFIC STYLES --- */
    .login-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        margin-top: 6rem;
    }

    .login-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 2.5rem 2rem;
        box-shadow: 0 4px 40px rgba(0,0,0,0.3);
        width: 100%;
        max-width: 420px;
        margin: 0 auto;
    }

    .divider {
        display: flex;
        align-items: center;
        text-align: center;
        margin: 1.5rem 0;
        color: var(--text-secondary);
        font-size: 0.8rem;
    }
    
    .divider::before, .divider::after {
        content: '';
        flex: 1;
        border-bottom: 1px solid var(--border-color);
    }
    
    .divider:not(:empty)::before { margin-right: .5em; }
    .divider:not(:empty)::after { margin-left: .5em; }

    .footer-links {
        text-align: center;
        margin-top: 1.5rem;
        font-size: 0.85rem;
        color: var(--text-secondary);
    }
    
    .footer-links a {
        color: #00D9C0;
        text-decoration: none;
        font-weight: 600;
    }

    /* --- DASHBOARD SPECIFIC STYLES --- */
    
    
    section[data-testid="stSidebar"] {
        position: relative;
        z-index: 1;
        background: linear-gradient(180deg, #0D1220 0%, #0A0E18 100%);
        border-right: 1px solid var(--border-color);
    }

    section[data-testid="stSidebar"] .stButton button {
        width: 100%;
        display: flex !important;
        justify-content: flex-start !important;
        align-items: center;
        text-align: left !important;
        background: transparent;
        border: 1px solid transparent;
        color: var(--text-secondary);
        font-weight: 500;
        font-size: 0.92rem;
        padding: 0.62rem 0.85rem;
        border-radius: 10px;
        transition: all 0.15s ease-in-out;
        margin-bottom: 2px;
    }

    section[data-testid="stSidebar"] .stButton button p {
        text-align: left !important;
        width: 100%;
    }

    section[data-testid="stSidebar"] .stButton button:hover {
        background: rgba(108, 92, 231, 0.12);
        color: var(--text-primary);
        border: 1px solid rgba(108, 92, 231, 0.28);
        transform: translateX(2px);
    }

    section[data-testid="stSidebar"] .stButton button[kind="primary"] {
        display: flex !important;
        justify-content: flex-start !important;
        background: linear-gradient(90deg, rgba(108,92,231,0.22), rgba(0,217,192,0.08)) !important;
        border: 1px solid rgba(108,92,231,0.45) !important;
        color: var(--text-primary) !important;
        font-weight: 600;
        box-shadow: inset 3px 0 0 var(--accent-2);
    }

    section[data-testid="stSidebar"] .stButton button[kind="primary"]:hover {
        transform: none;
        background: linear-gradient(90deg, rgba(108,92,231,0.28), rgba(0,217,192,0.1)) !important;
    }

    .card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.3rem 1.4rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
        transition: transform 0.18s ease, box-shadow 0.18s ease, border-color 0.18s ease;
    }
    
    .glass-card{
        background:rgba(22,28,44,.72);
        backdrop-filter:blur(18px);
        border:1px solid rgba(255,255,255,.08);
        border-radius:20px;
        padding:1.5rem;
        box-shadow:0 12px 40px rgba(0,0,0,.28);
    }
    
    .card:hover {
        transform: translateY(-3px);
        border-color: rgba(108, 92, 231, 0.4);
        box-shadow: 0 10px 30px rgba(108, 92, 231, 0.15);
    }

    .avatar-badge {
        width: 34px;
        height: 34px;
        min-width: 34px;
        border-radius: 50%;
        background: linear-gradient(135deg, #6C5CE7, #00D9C0);
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.85rem;
        color: #0B0F19;
    }

    .metric-icon {
        width: 32px;
        height: 32px;
        border-radius: 9px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1rem;
        margin-bottom: 0.5rem;
    }

    h1, h2, h3 {
        font-family: 'Sora', sans-serif;
        letter-spacing: -0.02em;
    }

    .brand-title {
        font-family: 'Sora', sans-serif;
        font-weight: 800;
        font-size: 1.6rem;
        background: linear-gradient(90deg, #A78BFA, #00D9C0);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0;
        text-align: center;
    }
    
    /* Override for sidebar */
    section[data-testid="stSidebar"] .brand-title {
        font-size: 1.35rem;
        text-align: left;
    }

    .brand-sub {
        color: var(--text-secondary);
        font-size: 0.85rem;
        margin-top: -2px;
        letter-spacing: 0.04em;
        text-align: center;
    }
    
    /* Override for sidebar */
    section[data-testid="stSidebar"] .brand-sub {
        font-size: 0.78rem;
        margin-top: -6px;
        text-align: left;
        text-transform: uppercase;
    }

    .page-header {
        display: flex;
        align-items: center;
        gap: 14px;
        margin-bottom: 0.2rem;
    }

    .page-header .icon-badge {
        width: 46px;
        height: 46px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.4rem;
        background: linear-gradient(135deg, rgba(108,92,231,0.25), rgba(0,217,192,0.15));
        border: 1px solid rgba(108,92,231,0.35);
    }

    .page-subtitle {
        color: var(--text-secondary);
        font-size: 0.95rem;
        margin-top: 4px;
        margin-bottom: 1.6rem;
    }

    .hero-panel{
        background:linear-gradient(
            120deg,
            rgba(108,92,231,.18),
            rgba(0,217,192,.12)
        );
        border-radius:24px;
        padding:2.5rem;
        margin-bottom:2rem;
    }
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border-color);
        border-radius: 16px;
        padding: 1.1rem 1.3rem;
        text-align: left;
    }

    .metric-label {
        color: var(--text-secondary);
        font-size: 0.82rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 600;
    }

    .metric-value {
        font-family: 'Sora', sans-serif;
        font-size: 1.9rem;
        font-weight: 700;
        margin-top: 2px;
    }

    .metric-delta-up { color: var(--accent-2); font-size: 0.85rem; font-weight: 600; }
    .metric-delta-down { color: #FB7185; font-size: 0.85rem; font-weight: 600; }

    .pill {
        display: inline-block;
        padding: 3px 12px;
        border-radius: 999px;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.03em;
    }

    .pill-easy { background: rgba(0,217,192,0.15); color: #00D9C0; }
    .pill-medium { background: rgba(255,176,32,0.15); color: #FFB020; }
    .pill-hard { background: rgba(251,113,133,0.15); color: #FB7185; }

    .flashcard {
        background: linear-gradient(135deg, #1B2136 0%, #131829 100%);
        border: 1px solid rgba(108,92,231,0.35);
        border-radius: 20px;
        padding: 2.4rem 2rem;
        min-height: 220px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text-primary);
        box-shadow: 0 10px 40px rgba(108,92,231,0.15);
    }

    .flash-tag {
        color: var(--text-secondary);
        font-size: 0.78rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.6rem;
        font-weight: 600;
    }
    .flip-card {
        perspective: 1200px;
        height: 240px;
        margin-bottom: 1rem;
    }

    .flip-card-inner {
        position: relative;
        width: 100%;
        height: 100%;
        transition: transform 0.6s cubic-bezier(0.4, 0.2, 0.2, 1);
        transform-style: preserve-3d;
    }

    .flip-card-inner.is-flipped {
        transform: rotateY(180deg);
    }

    .flip-card-face {
        position: absolute;
        inset: 0;
        backface-visibility: hidden;
        -webkit-backface-visibility: hidden;
        border-radius: 20px;
        display: flex;
        align-items: center;
        justify-content: center;
        text-align: center;
        padding: 2rem;
        box-shadow: 0 10px 40px rgba(108,92,231,0.15);
    }

    .flip-card-front {
        background: linear-gradient(135deg, #1B2136 0%, #131829 100%);
        border: 1px solid rgba(108,92,231,0.35);
        color: var(--text-primary);
    }

    .flip-card-back {
        background: linear-gradient(135deg, #202A45 0%, #16324A 100%);
        border: 1px solid rgba(0,217,192,0.35);
        color: var(--text-primary);
        transform: rotateY(180deg);
    }

    .flip-card-content {
        font-size: 1.2rem;
        font-weight: 600;
        line-height: 1.5;
    }
    .chat-bubble-user {
        background:linear-gradient(
            135deg,
            #6C5CE7,
            #8B7BF0
        );
        border-radius:18px;
        padding:1rem 1.2rem;
        margin-left:auto;
        margin-bottom:.8rem;
        color:white;
    }

    .chat-bubble-bot {
        background:#141B2A;
        border:1px solid rgba(255,255,255,.06);
        border-radius:18px;
        padding:1rem 1.2rem;
        margin-bottom:.8rem;
        box-shadow:0 4px 18px rgba(0,0,0,.18);
    }
    
    .chat-container{
        height:65vh;
        overflow-y:auto;
        padding-right:8px;
    }
    
    .chat-input-container{
        position:sticky;
        bottom:0;
        background:rgba(11,15,25,.9);
        padding:1rem 0;
        backdrop-filter:blur(15px);
    }
    
    /* Upload Area */

    .stFileUploader{
        border:none !important;
    }

    .stFileUploader > div{
        background:rgba(22,28,44,.75);
        border:2px dashed rgba(108,92,231,.35);
        border-radius:22px;
        padding:2rem;
        transition:.25s;
    }

    .stFileUploader > div:hover{
        border-color:#00D9C0;
        background:rgba(0,217,192,.05);
    }
    
    /* Expanders */

    .streamlit-expanderHeader{
        font-weight:600;
        color:white;
    }

    div[data-testid="stExpander"]{
        border-radius:18px;
        border:1px solid rgba(255,255,255,.08);
        background:#161C2C;
    }
    
    /* Tabs */

    button[data-baseweb="tab"]{
        border-radius:12px !important;
        font-weight:600;
    }

    button[data-baseweb="tab"][aria-selected="true"]{
        background:#6C5CE7 !important;
        color:white !important;
    }

    /* Spinner */

    .stSpinner{
        color:#6C5CE7;
    }
    
    div[data-baseweb="notification"]{
        border-radius:16px;
    }
    
    [data-testid="column"]{
        padding-left:.4rem;
        padding-right:.4rem;
    }
    .divider-line {
        border-top: 1px solid var(--border-color);
        margin: 1.4rem 0;
    }

    .footer-note {
        color: var(--text-secondary);
        font-size: 0.78rem;
        text-align: center;
        margin-top: 3rem;
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {
        background-color: #10152355 !important;
        border-radius: 10px !important;
        color: white !important;
    }
    
    .stTextInput input:focus {
        border-color: #6C5CE7 !important;
        box-shadow: 0 0 0 1px #6C5CE7 !important;
    }

    .stButton>button[kind="primary"] {
        background: linear-gradient(90deg, #6C5CE7, #8B7BF0);
        border: none;
        border-radius: 10px;
        font-weight: 600;
        padding: 0.55rem 1.3rem;
        transition: transform 0.15s ease;
    }
    
    .stButton>button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(108, 92, 231, 0.4);
    }

    .stButton>button[kind="secondary"] {
        border-radius: 10px;
        font-weight: 600;
    }

    .progress-track {
        background: #1E2536;
        border-radius: 999px;
        height: 8px;
        width: 100%;
        overflow: hidden;
    }
    .progress-fill {
        background: linear-gradient(90deg, #6C5CE7, #00D9C0);
        height: 8px;
        border-radius: 999px;
    }
    ::-webkit-scrollbar{
        width:8px;
    }

    ::-webkit-scrollbar-thumb{
        background:#6C5CE7;
        border-radius:20px;
    }
    
    .typing{
        display:flex;
        gap:4px;
    }

    .typing span{
        width:7px;
        height:7px;
        border-radius:50%;
        background:#00D9C0;
        animation:blink 1.4s infinite;
    }

    .typing span:nth-child(2){
        animation-delay:.2s;
    }

    .typing span:nth-child(3){
        animation-delay:.4s;
    }

    .muted {
        color: #94A3B8;
        font-size: 0.95rem;
    }
    @keyframes blink{

        0%{
            opacity:.2;
        }

        50%{
            opacity:1;
        }

        100%{
            opacity:.2;
        }

    }
</style>
"""

def apply_styles() -> None:
    st.markdown(CSS, unsafe_allow_html=True)
