import streamlit as st
import tempfile
import os
from moviepy.editor import VideoFileClip


from sidebar import show_sidebar
show_sidebar()

st.set_page_config(page_title="Video Tools", page_icon="🎬", layout="centered")

st.title("🎬 Video Lite: Trim, GIF & Audio")
st.write("Secure, in-memory video processing. No files are permanently saved.")

# --- 1. FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload a Video", type=["mp4", "mov", "avi"])

if uploaded_file:
    # Save the uploaded file to a temporary file so moviepy can read it
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as temp_video:
        temp_video.write(uploaded_file.read())
        video_path = temp_video.name

    try:
        # Load video to get its duration
        clip = VideoFileClip(video_path)
        duration = clip.duration

        # --- 2. TRIM CONTROLS ---
        st.markdown("### ✂️ Trim Your Video")
        start_time, end_time = st.slider(
            "Select the start and end time (in seconds)",
            min_value=0.0,
            max_value=duration,
            value=(0.0, duration),
            step=0.1
        )

        st.markdown("---")

        # --- 3. PROCESSING OPTIONS ---
        st.markdown("### ⚙️ Choose Action")
        action = st.radio("What would you like to do?", ["Extract Audio (MP3)", "Convert to GIF"])
        
        # GIF Settings (Only show if GIF is selected)
        gif_fps = 10
        if action == "Convert to GIF":
            st.warning("Note: High framerates create massive GIF files. 10 to 15 FPS is recommended.")
            gif_fps = st.slider("GIF Framerate (FPS)", min_value=5, max_value=30, value=10)

        # --- 4. EXECUTION ---
        if st.button("🚀 Process Video", type="primary"):
            with st.spinner("Processing... This might take a minute for larger files."):
                
                # Apply the trim
                trimmed_clip = clip.subclip(start_time, end_time)

                if action == "Extract Audio (MP3)":
                    # Create a temporary file for the MP3
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
                        output_path = temp_audio.name
                    
                    # Write the audio
                    trimmed_clip.audio.write_audiofile(output_path, logger=None)
                    
                    # Read back as bytes for download
                    with open(output_path, "rb") as f:
                        output_bytes = f.read()
                    
                    st.success("✅ Audio Extracted Successfully!")
                    st.download_button("📥 Download MP3", output_bytes, file_name="extracted_audio.mp3", mime="audio/mp3")

                elif action == "Convert to GIF":
                    # Create a temporary file for the GIF
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".gif") as temp_gif:
                        output_path = temp_gif.name
                    
                    # Write the GIF
                    trimmed_clip.write_gif(output_path, fps=gif_fps, logger=None)
                    
                    # Read back as bytes for download
                    with open(output_path, "rb") as f:
                        output_bytes = f.read()
                    
                    st.success("✅ GIF Created Successfully!")
                    st.image(output_bytes) # Show a preview of the GIF
                    st.download_button("📥 Download GIF", output_bytes, file_name="converted_video.gif", mime="image/gif")

                # Clean up the output temp file
                os.remove(output_path)
                
    except Exception as e:
        st.error(f"An error occurred: {e}")
        
    finally:
        # Clean up the initial uploaded temp file so we don't leak memory!
        clip.close()
        if os.path.exists(video_path):
            os.remove(video_path)