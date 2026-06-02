import streamlit as st

st.set_page_config(page_title="Universal Utility Suite", page_icon="🛠️", layout="centered")

st.markdown("<h1 style='text-align: center;'>🛠️ Universal Utility Suite</h1>", unsafe_allow_html=True)
st.markdown("<h4 style='text-align: center; color: #555; padding-bottom: 2rem;'>Fast, private, in-memory processing. Select a toolkit below to get started.</h4>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center;'>📄</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>PDF Tools</h3>", unsafe_allow_html=True)
        st.write("Merge, compress, split, convert, and secure your documents.")
        st.write("") # Spacer
        st.page_link("pages/1_pdf_tools.py", label="Open PDF Tools", icon="🚀", use_container_width=True)

with col2:
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center;'>🖼️</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Image Tools</h3>", unsafe_allow_html=True)
        st.write("Batch resize, compress, and convert image formats easily.")
        st.write("") # Spacer
        st.page_link("pages/2_image_tools.py", label="Open Image Tools", icon="🚀", use_container_width=True)

with col3:
    with st.container(border=True):
        st.markdown("<h1 style='text-align: center;'>🎬</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center;'>Video Tools</h3>", unsafe_allow_html=True)
        st.write("Trim, extract audio, and create GIFs from your videos.")
        st.write("") # Spacer
        st.page_link("pages/3_video_tools.py", label="Open Video Tools", icon="🚀", use_container_width=True)