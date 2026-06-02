import streamlit as st

def show_sidebar():
    with st.sidebar:
        st.markdown("### 🛠️ Utility Suite")
        st.write("---")
        
        st.markdown("""
            <style>
            /* Force the button to be compact */
            [data-testid="stSidebar"] div.stButton > button {
                min-height: 40px !important; /* Shrinks the vertical size */
                height: 40px !important;
                width: 100% !important;
                justify-content: flex-start !important;
                padding: 0 10px !important;
                background-color: transparent !important;
                border: none !important;
                border-radius: 5px !important;
                text-align: left !important;
            }
            
            /* Add hover effect only */
            [data-testid="stSidebar"] div.stButton > button:hover {
                background-color: rgba(255, 255, 255, 0.1) !important;
            }
            
            /* Shrink text */
            [data-testid="stSidebar"] div.stButton > button p {
                font-size: 14px !important;
                margin: 0 !important;
            }
            </style>
        """, unsafe_allow_html=True)
        
        if st.button("🏠 Home"):
            st.switch_page("app.py")
            
        st.markdown("#### 📁 Tools")
        if st.button("📄 PDF Tools"):
            st.switch_page("pages/1_pdf_tools.py")
        if st.button("🖼️ Image Tools"):
            st.switch_page("pages/2_image_tools.py")
        if st.button("🎬 Video Trimmer"):
            st.switch_page("pages/3_video_tools.py")
        if st.button("🔻 Media Downloader"):
            st.switch_page("pages/4_youtube_tools.py")
            
        st.write("---")
        st.caption("Universal Utility Suite © 2026")