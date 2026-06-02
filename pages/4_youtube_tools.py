import streamlit as st
import yt_dlp
import tempfile
import os
import requests
import re
import subprocess

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

use_api = st.toggle("Use API Fallback (Enable if downloads are blocked)", value=False)

if use_api:
    st.warning("⚠️ **API Mode enabled:** This will consume your monthly API request quota.")
else:
    st.info("✅ **Standard Mode:** Using free yt-dlp processing.")

# --- 3. EXECUTE LOGIC ---
if url:
    info = {}
    is_instagram = "instagram.com" in url.lower()
    api_error_triggered = False
    
    # --- SAFE CREDENTIAL PARSING ---
    default_key = "e68e29e6d8msh26ce30d7159259cp1cce24jsncbfc81dfcc64"
    try:
        api_key = st.secrets.get("RAPIDAPI_KEY", default_key)
    except Exception:
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
                yt_id_match = re.search(r'(?:v=|/v/|youtu\.be/|/embed/|/shorts/)([\w-]{11})', url)
                video_id = yt_id_match.group(1) if yt_id_match else url
                
                response = requests.get(api_url, headers=headers, params={"videoId": video_id})
                response_data = response.json()
                
                if response.status_code == 200 and response_data.get("errorId") == "Success":
                    info['title'] = response_data.get('title', 'API Managed Media')
                    info['duration'] = int(response_data.get('lengthSeconds', 0))
                    
                    thumbnails = response_data.get("thumbnails", [])
                    if thumbnails:
                        info['thumbnail'] = thumbnails[-1].get("url", "")
                    else:
                        info['thumbnail'] = ""
                    
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
                            cached_api_data = st.session_state.get("api_response", {})
                            safe_title = "".join([c for c in info.get('title', 'video') if c.isalpha() or c.isdigit() or c==' ']).rstrip()
                            
                            # Disguise the Python request as a normal Web Browser so Google doesn't block the download
                            browser_headers = {
                                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
                            }
                            
                            # --- AUDIO ONLY ---
                            if "Audio Only" in quality_choice:
                                audio_items = cached_api_data.get("audios", {}).get("items", [])
                                if audio_items:
                                    download_url = audio_items[0].get("url")
                                    with st.spinner("Routing audio file for direct download..."):
                                        try:
                                            audio_resp = requests.get(download_url, headers=browser_headers, stream=True, timeout=15)
                                            st.download_button(
                                                label="📥 Click Here to Download Audio",
                                                data=audio_resp.content,
                                                file_name=f"{safe_title}.m4a",
                                                mime="audio/mp4",
                                                use_container_width=True
                                            )
                                        except Exception as e:
                                            st.error("❌ Failed to download audio from Google servers.")
                                else:
                                    st.error("❌ Could not locate an audio stream.")
                            
                            # --- VIDEO ---
                            else:
                                video_items = cached_api_data.get("videos", {}).get("items", [])
                                audio_items = cached_api_data.get("audios", {}).get("items", [])
                                
                                target_quality = "360p"
                                if "1080p" in quality_choice: target_quality = "1080p"
                                elif "720p" in quality_choice: target_quality = "720p"
                                elif "480p" in quality_choice: target_quality = "480p"

                                best_video = None
                                for item in video_items:
                                    if item.get("quality") == target_quality and item.get("extension") == "mp4":
                                        best_video = item
                                        break
                                        
                                if not best_video and video_items:
                                    best_video = next((i for i in video_items if i.get("extension") == "mp4"), video_items[0])

                                if best_video:
                                    # SCENARIO A: Low Quality / Native Audio (Bypasses Merge)
                                    if best_video.get("hasAudio"):
                                        with st.spinner("Routing video file for direct download..."):
                                            try:
                                                video_resp = requests.get(best_video.get("url"), headers=browser_headers, stream=True, timeout=15)
                                                st.download_button(
                                                    label="📥 Click Here to Download Video",
                                                    data=video_resp.content,
                                                    file_name=f"{safe_title}.mp4",
                                                    mime="video/mp4",
                                                    use_container_width=True
                                                )
                                            except Exception as e:
                                                st.error("❌ Failed to download video from Google servers.")
                                    
                                    # SCENARIO B: High Quality 1080p (Requires FFmpeg Muxing)
                                    else:
                                        best_audio = audio_items[0] if audio_items else None
                                        if best_audio:
                                            st.info("Starting High-Quality Compilation...")
                                            progress_bar = st.progress(0)
                                            
                                            with tempfile.TemporaryDirectory() as temp_dir:
                                                vid_path = os.path.join(temp_dir, "vid.mp4")
                                                aud_path = os.path.join(temp_dir, "aud.m4a")
                                                out_path = os.path.join(temp_dir, f"{safe_title}.mp4")
                                                
                                                try:
                                                    # Step 1: Pre-download Video (Using large 1MB chunks)
                                                    st.write(f"📥 1/3 Downloading {best_video.get('quality')} video track...")
                                                    v_res = requests.get(best_video.get("url"), headers=browser_headers, stream=True, timeout=15)
                                                    with open(vid_path, "wb") as f:
                                                        for chunk in v_res.iter_content(chunk_size=1024 * 1024):
                                                            if chunk: f.write(chunk)
                                                    progress_bar.progress(33)
                                                                
                                                    # Step 2: Pre-download Audio
                                                    st.write("📥 2/3 Downloading audio track...")
                                                    a_res = requests.get(best_audio.get("url"), headers=browser_headers, stream=True, timeout=15)
                                                    with open(aud_path, "wb") as f:
                                                        for chunk in a_res.iter_content(chunk_size=1024 * 1024):
                                                            if chunk: f.write(chunk)
                                                    progress_bar.progress(66)
                                                                
                                                    # Step 3: Fast Local Merge
                                                    st.write("🔄 3/3 Merging tracks together...")
                                                    cmd = [
                                                        "ffmpeg", "-y",
                                                        "-i", vid_path,
                                                        "-i", aud_path,
                                                        "-c", "copy",
                                                        out_path
                                                    ]
                                                    
                                                    # Run ffmpeg
                                                    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                                    progress_bar.progress(100)
                                                    
                                                    with open(out_path, "rb") as f:
                                                        st.success("✅ High-Quality merge complete!")
                                                        st.download_button(
                                                            label="📥 Save Final HD Video to Device",
                                                            data=f.read(),
                                                            file_name=f"{safe_title}.mp4",
                                                            mime="video/mp4",
                                                            use_container_width=True
                                                        )
                                                        
                                                except requests.exceptions.RequestException as e:
                                                    st.error(f"❌ Network timeout connecting to Google Servers. Please try again.")
                                                except FileNotFoundError:
                                                    st.error("❌ System Error: FFmpeg is not installed on this machine. (Required for 1080p merges).")
                                                except subprocess.CalledProcessError:
                                                    st.error("❌ FFmpeg failed to merge the tracks.")
                                        else:
                                            st.error("❌ Found high-quality video, but no audio track to merge.")
                                else:
                                    st.error("❌ Could not locate a compatible video stream.")
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