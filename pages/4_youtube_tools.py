import streamlit as st
import yt_dlp
import tempfile
import os
import requests
import re

# Config must be called before everything else
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

# --- 2. DOWNLOAD MODE TOGGLE ---
st.markdown("### ⚙️ Download Settings")

# Toggle between Free (yt-dlp) and API (Fallback)
use_api = st.toggle("Use API Fallback (Enable if downloads are blocked)", value=False)

if use_api:
    st.warning("⚠️ **API Mode enabled:** This will consume your monthly API request quota.")
else:
    st.info("✅ **Standard Mode:** Using free yt-dlp processing.")

# --- 3. EXECUTE LOGIC ---
if url:
    # We will store parsed media information here globally for the UI
    info = {}
    is_instagram = "instagram.com" in url.lower()
    api_error_triggered = False
    
    # --- SAFE CREDENTIAL PARSING ---
    default_key = "e68e29e6d8msh26ce30d7159259cp1cce24jsncbfc81dfcc64"
    try:
        api_key = st.secrets.get("RAPIDAPI_KEY", default_key)
    except Exception:
        # Fallback to hardcoded key if secrets subsystem isn't initialized locally
        api_key = default_key

    headers = {
        "x-rapidapi-key": api_key,
        "x-rapidapi-host": "youtube-media-downloader.p.rapidapi.com",
        "Content-Type": "application/json"
    }
    api_url = "https://youtube-media-downloader.p.rapidapi.com/v2/video/details"

    with st.spinner("Fetching media info..."):
        try:
            if use_api:
                # ==========================================
                # METADATA FETCH: API MODE
                # ==========================================
                # 1. Extract the unique 11-character video ID from the YouTube URL
                yt_id_match = re.search(r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([\w-]{11})', url)
                video_id = yt_id_match.group(1) if yt_id_match else url
                
                # 2. Use 'videoId' parameter instead of 'url' as required by RapidAPI
                response = requests.get(api_url, headers=headers, params={"videoId": video_id})
                response_data = response.json()
                
                # Check for "Success" based on the exact JSON payload provided
                if response.status_code == 200 and response_data.get("errorId") == "Success":
                    
                    info['title'] = response_data.get('title', 'API Managed Media')
                    info['duration'] = int(response_data.get('lengthSeconds', 0))
                    
                    # Safely grab the highest quality thumbnail
                    thumbnails = response_data.get("thumbnails", [])
                    if thumbnails:
                        info['thumbnail'] = thumbnails[-1].get("url", "")
                    else:
                        info['thumbnail'] = ""
                    
                    # Stash response data in session state to pass to the downloader block
                    st.session_state["api_response"] = response_data
                else:
                    api_error_triggered = True
                    st.error("❌ The API was unable to fetch details for this video URL.")
                    with st.expander("View Diagnostic API Data"):
                        st.json(response_data)
            else:
                # ==========================================
                # METADATA FETCH: STANDARD MODE (yt-dlp)
                # ==========================================
                ydl_opts_info = {'quiet': True, 'extract_flat': False}
                with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
                    info = ydl.extract_info(url, download=False)

            # --- 4. DISPLAY COMPONENT INTERFACE ---
            if not api_error_triggered:
                col_img, col_text = st.columns([1, 2])
                with col_img:
                    if info.get('thumbnail'):
                        st.image(info.get('thumbnail'), use_container_width=True)
                with col_text:
                    st.subheader(info.get('title', info.get('description', 'Media Item')))
                    
                    duration = info.get('duration')
                    if duration:
                        minutes, seconds = divmod(int(duration), 60)
                        if duration > MAX_VIDEO_LENGTH_SECONDS:
                            st.markdown(f"**Length:** :red[{minutes}:{seconds:02d} (Too Long)]")
                        else:
                            st.write(f"**Length:** {minutes}:{seconds:02d}")

                st.markdown("---")
                
                # --- 5. DOWNLOAD OPTIONS MENU ---
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
                    if duration and duration > MAX_VIDEO_LENGTH_SECONDS:
                        st.error("❌ Video is too long! Limit is 60 minutes.")
                    else:
                        if use_api:
                            # ==========================================
                            # DOWNLOAD: API MODE
                            # ==========================================
                            with st.spinner("Processing download via RapidAPI..."):
                                cached_api_data = st.session_state.get("api_response", {})
                                
                                download_url = None
                                
                                # If User Wants Audio Only
                                if "Audio Only" in quality_choice:
                                    audio_items = cached_api_data.get("audios", {}).get("items", [])
                                    if audio_items:
                                        # Grab the first available audio stream
                                        download_url = audio_items[0].get("url")
                                        mime_type = "audio/mp4"
                                        ext = "m4a"
                                
                                # If User Wants Video
                                else:
                                    video_items = cached_api_data.get("videos", {}).get("items", [])
                                    
                                    # Very basic resolution matching logic based on the payload
                                    target_quality = "360p" # fallback
                                    if "1080p" in quality_choice: target_quality = "1080p"
                                    elif "720p" in quality_choice: target_quality = "720p"
                                    elif "480p" in quality_choice: target_quality = "480p"

                                    for item in video_items:
                                        if item.get("quality") == target_quality and item.get("extension") == "mp4":
                                            download_url = item.get("url")
                                            break
                                    
                                    # If the exact resolution isn't found, grab the very first mp4 available
                                    if not download_url and video_items:
                                        for item in video_items:
                                             if item.get("extension") == "mp4":
                                                download_url = item.get("url")
                                                break

                                    mime_type = "video/mp4"
                                    ext = "mp4"

                                if download_url:
                                    st.success("✅ Download link verified!")
                                    
                                    # Provide the direct link as an HTML button for the user to download instantly
                                    # Streaming large files through Streamlit's memory can cause server crashes,
                                    # so we provide the raw API url directly to the user's browser.
                                    
                                    safe_title = "".join([c for c in info.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                                    
                                    st.markdown(
                                        f'<a href="{download_url}" download="{safe_title}.{ext}" target="_blank">'
                                        f'<button style="width:100%; background-color:#FF4B4B; color:white; border:none; padding:10px; border-radius:5px; cursor:pointer;">'
                                        f'📥 Click Here to Save to Device'
                                        f'</button></a>',
                                        unsafe_allow_html=True
                                    )
                                else:
                                    st.error("❌ Could not locate a compatible media stream for this resolution.")
                                    with st.expander("View Diagnostic API Data"):
                                        st.json(cached_api_data)
                        else:
                            # ==========================================
                            # DOWNLOAD: STANDARD MODE (yt-dlp)
                            # ==========================================
                            with st.spinner("Processing with FFmpeg..."):
                                with tempfile.TemporaryDirectory() as temp_dir:
                                    out_tmpl = os.path.join(temp_dir, '%(title)s.%(ext)s')
                                    
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
                                        if "2160p" in quality_choice: res = "2160"
                                        elif "1080p" in quality_choice: res = "1080"
                                        elif "720p" in quality_choice: res = "720"
                                        else: res = "480"
                                        
                                        format_str = f'bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[height<={res}][ext=mp4]/best'
                                        ydl_opts = {'format': format_str, 'outtmpl': out_tmpl, 'merge_output_format': 'mp4', 'quiet': True}
                                        mime_type = "video/mp4"

                                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                                        ydl.download([url])

                                    final_files = [f for f in os.listdir(temp_dir) if not f.endswith('.part')]
                                    if final_files:
                                        with open(os.path.join(temp_dir, final_files[0]), "rb") as f:
                                            st.success("✅ Ready!")
                                            st.download_button("📥 Save to Device", f.read(), final_files[0], mime=mime_type)
                                    else:
                                        st.error("Error: Could not locate the file.")
                                        
        except yt_dlp.utils.DownloadError as e:
            if "bot" in str(e) or "cookies" in str(e) or "403" in str(e):
                st.error("❌ YouTube blocked the connection attempt via Standard Mode.")
                st.info("💡 **Keep the 'Use API Fallback' switch active to avoid this system block!**")
            else:
                st.error(f"❌ Error processing link: {e}")
        except Exception as e:
            st.error(f"❌ An unexpected runtime error occurred: {e}")