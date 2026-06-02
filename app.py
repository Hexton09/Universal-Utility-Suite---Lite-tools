import streamlit as st

from sidebar import show_sidebar
show_sidebar()

st.set_page_config(page_title="Universal Utility Suite", page_icon="🛠️", layout="centered")

# --- Custom CSS for Bulletproof Color-Coded Tile Buttons ---
st.markdown("""
    <style>
    .title-text { text-align: center; padding-top: 2rem; padding-bottom: 1rem; }
    .subtitle-text { text-align: center; color: var(--text-color); opacity: 0.8; padding-bottom: 3rem; }
    
    /* 1. Target the button itself using its core attribute */
    button[kind="secondary"] {
        min-height: 250px !important;
        height: auto !important;
        width: 100% !important;
        border: 2px solid rgba(128, 128, 128, 0.2) !important;
        border-radius: 12px !important;
        background-color: var(--secondary-background-color) !important; 
        transition: all 0.3s ease-in-out !important;
        padding: 20px !important;
    }
    
    /* Hover Lift */
    button[kind="secondary"]:hover {
        transform: translateY(-5px) !important;
    }
    
    /* 2. Force the text inside to inherit formatting and wrap properly */
    button[kind="secondary"] p,
    button[kind="secondary"] strong {
        font-size: 1.15rem !important;
        white-space: normal !important; 
        text-align: center !important;
        line-height: 1.6 !important;
        color: var(--text-color) !important;
        transition: color 0.3s ease-in-out !important;
    }

    /* ======================================================
       COLOR CODED HOVER EFFECTS 
       (Catches all past and present Streamlit Column names)
       ====================================================== */
       
    /* --- PDF Tools (Column 1) -> RED Hover --- */
    div[data-testid="stColumn"]:nth-of-type(1) button[kind="secondary"]:hover,
    div[data-testid="column"]:nth-of-type(1) button[kind="secondary"]:hover,
    div[data-testid="stVerticalBlock"]:nth-of-type(1) button[kind="secondary"]:hover {
        border-color: #ff4b4b !important;
        box-shadow: 0 8px 16px rgba(255, 75, 75, 0.2) !important;
    }
    div[data-testid="stColumn"]:nth-of-type(1) button[kind="secondary"]:hover *,
    div[data-testid="column"]:nth-of-type(1) button[kind="secondary"]:hover *,
    div[data-testid="stVerticalBlock"]:nth-of-type(1) button[kind="secondary"]:hover * {
        color: #ff4b4b !important; 
    }

    /* --- Image Tools (Column 2) -> YELLOW Hover --- */
    div[data-testid="stColumn"]:nth-of-type(2) button[kind="secondary"]:hover,
    div[data-testid="column"]:nth-of-type(2) button[kind="secondary"]:hover,
    div[data-testid="stVerticalBlock"]:nth-of-type(2) button[kind="secondary"]:hover {
        border-color: #fca311 !important; 
        box-shadow: 0 8px 16px rgba(252, 163, 17, 0.2) !important;
    }
    div[data-testid="stColumn"]:nth-of-type(2) button[kind="secondary"]:hover *,
    div[data-testid="column"]:nth-of-type(2) button[kind="secondary"]:hover *,
    div[data-testid="stVerticalBlock"]:nth-of-type(2) button[kind="secondary"]:hover * {
        color: #fca311 !important; 
    }

    /* --- Video Tools (Column 3) -> GREEN Hover --- */
    div[data-testid="stColumn"]:nth-of-type(3) button[kind="secondary"]:hover,
    div[data-testid="column"]:nth-of-type(3) button[kind="secondary"]:hover,
    div[data-testid="stVerticalBlock"]:nth-of-type(3) button[kind="secondary"]:hover {
        border-color: #09ab3b !important;
        box-shadow: 0 8px 16px rgba(9, 171, 59, 0.2) !important;
    }
    div[data-testid="stColumn"]:nth-of-type(3) button[kind="secondary"]:hover *,
    div[data-testid="column"]:nth-of-type(3) button[kind="secondary"]:hover *,
    div[data-testid="stVerticalBlock"]:nth-of-type(3) button[kind="secondary"]:hover * {
        color: #09ab3b !important; 
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>🛠️ Universal Utility Suite</h1>", unsafe_allow_html=True)
st.markdown("<h4 class='subtitle-text'>Fast, private, in-memory processing. Select a toolkit below to get started.</h4>", unsafe_allow_html=True)

# --- Tile Layout (2x2 Grid) ---
col1, col2 = st.columns(2)

with col1:
    if st.button("📄\n\n**PDF Tools**\n\nMerge, compress, split, convert, and secure your documents.", use_container_width=True):
        st.switch_page("pages/1_pdf_tools.py")
        
    if st.button("🎬\n\n**Video Tools**\n\nTrim, extract audio, and create GIFs from your videos.", use_container_width=True):
        st.switch_page("pages/3_video_tools.py")

with col2:
    if st.button("🖼️\n\n**Image Tools**\n\nBatch resize, compress, and convert image formats easily.", use_container_width=True):
        st.switch_page("pages/2_image_tools.py")
        
    if st.button("🔻\n\n**Media Downloader**\n\nExtract high-quality video or audio directly from YouTube.", use_container_width=True):
        st.switch_page("pages/4_youtube_tools.py")