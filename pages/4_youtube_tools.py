import streamlit as st
import yt_dlp
import tempfile
import os


from sidebar import show_sidebar
show_sidebar()

st.set_page_config(page_title="YouTube/Instagram Tools", page_icon="🔻", layout="centered")

st.title("🔻 Media Downloader")
st.write("Fast, serverless media extraction. Paste a link to get started.")

# --- MEMORY SAFEGUARDS ---
MAX_VIDEO_LENGTH_SECONDS = 3600  # 60 minutes

# --- 0. INITIALIZE SESSION STATE ---
if "yt_url" not in st.session_state:
    st.session_state.yt_url = ""

# --- 1. SEARCH BAR LAYOUT ---
st.markdown("### 🔗 Paste YouTube or Instagram URL")
col_input, col_btn = st.columns([4, 1])

with col_input:
    url_input = st.text_input("URL Input", label_visibility="collapsed", placeholder="https://youtube.com/... or https://instagram.com/...")

with col_btn:
    fetch_clicked = st.button("🔍 Fetch", use_container_width=True)

if fetch_clicked and url_input:
    st.session_state.yt_url = url_input
elif url_input and url_input != st.session_state.yt_url:
    st.session_state.yt_url = url_input

if not url_input:
    st.session_state.yt_url = ""

url = st.session_state.yt_url

# --- 2. EXECUTE LOGIC ---
if url:
    with st.spinner("Fetching media info..."):
        try:
            # --- 3. FETCH METADATA ---
            ydl_opts_info = {'quiet': True, 'extract_flat': False}
            with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                info = ydl.extract_info(url, download=False)
            
            is_instagram = "instagram.com" in url.lower()
            
            # Display Info
            col_img, col_text = st.columns([1, 2])
            with col_img:
                st.image(info.get('thumbnail', ''), use_container_width=True)
            with col_text:
                st.subheader(info.get('title', info.get('description', 'Media Item')))
                
                # Only show duration if it exists
                duration = info.get('duration')
                if duration:
                    minutes, seconds = divmod(int(duration), 60)
                    if duration > MAX_VIDEO_LENGTH_SECONDS:
                        st.markdown(f"**Length:** :red[{minutes}:{seconds:02d} (Too Long)]")
                    else:
                        st.write(f"**Length:** {minutes}:{seconds:02d}")

            st.markdown("---")
            
            # --- 4. DOWNLOAD SETTINGS ---
            st.markdown("### ⚙️ Download Options")
            
            if is_instagram:
                quality_choice = "Instagram High Quality"
                st.info("Detected Instagram link. Will download best available quality.")
            else:
                quality_choice = st.selectbox(
                    "Select Video Quality / Format:",
                    [
                        "Video: 2160p (4K UHD)", 
                        "Video: 1080p (Full HD)", 
                        "Video: 720p (HD)", 
                        "Video: 480p (Data Saver)",
                        "Audio Only: 192kbps (Standard)"
                    ]
                )

            if st.button("🚀 Download Media", type="primary"):
                # Safety Check
                if duration and duration > MAX_VIDEO_LENGTH_SECONDS:
                    st.error("❌ Video is too long! Limit is 60 minutes.")
                else:
                    with st.spinner("Processing with FFmpeg..."):
                        with tempfile.TemporaryDirectory() as temp_dir:
                            out_tmpl = os.path.join(temp_dir, '%(title)s.%(ext)s')
                            
                            # Determine settings based on site and quality
                            if is_instagram:
                                ydl_opts = {'format': 'best', 'outtmpl': out_tmpl, 'quiet': True}
                                mime_type = "video/mp4"
                            elif "Audio Only" in quality_choice:
                                ydl_opts = {
                                    'format': 'bestaudio/best',
                                    'outtmpl': out_tmpl,
                                    'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}],
                                    'quiet': True
                                }
                                mime_type = "audio/mpeg"
                            else:
                                # Logic for YouTube video resolutions
                                if "2160p" in quality_choice: res = "2160"
                                elif "1080p" in quality_choice: res = "1080"
                                elif "720p" in quality_choice: res = "720"
                                else: res = "480"
                                
                                format_str = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'
                                ydl_opts = {'format': format_str, 'outtmpl': out_tmpl, 'merge_output_format': 'mp4', 'quiet': True}
                                mime_type = "video/mp4"

                            # Download
                            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                ydl.download([url])

                            final_files = [f for f in os.listdir(temp_dir) if not f.endswith('.part')]
                            if final_files:
                                with open(os.path.join(temp_dir, final_files[0]), "rb") as f:
                                    st.success("✅ Ready!")
                                    st.download_button("📥 Save to Device", f.read(), final_files[0], mime=mime_type)
                            else:
                                st.error("Error: Could not locate the file.")
        except Exception as e:
            st.error(f"❌ Error processing link: {e}")