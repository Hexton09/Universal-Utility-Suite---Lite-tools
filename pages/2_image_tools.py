import streamlit as st
from PIL import Image
import io
import zipfile

from sidebar import show_sidebar
show_sidebar()

st.set_page_config(page_title="Image Tools", page_icon="🖼️", layout="centered")

st.title("🖼️ Image Compressor & Resizer")
st.write("Choose your operations, configure your settings, and click process!")

# --- 1. SETTINGS ---
st.markdown("### ⚙️ Operations & Settings")

col1, col2 = st.columns(2)

with col1:
    compress_enabled = st.checkbox("🗜️ Compress File Size", value=True, key="img_comp_check")
    target_kb = None
    if compress_enabled:
        target_kb = st.number_input("Target Size per Image (KB)", min_value=5, max_value=5000, value=50, key="img_target_kb")

with col2:
    resize_enabled = st.checkbox("📏 Resize Pixel Dimensions", value=False, key="img_resize_check")
    new_width = None
    new_height = None
    if resize_enabled:
        sub_col1, sub_col2 = st.columns(2)
        with sub_col1:
            new_width = st.number_input("Max Width (px)", min_value=10, value=1000, key="img_max_w")
        with sub_col2:
            new_height = st.number_input("Max Height (px)", min_value=10, value=1000, key="img_max_h")

st.markdown("---")

# --- 2. FILE UPLOAD ---
uploaded_files = st.file_uploader("Drop images here (up to 10 recommended)", type=["jpg", "jpeg", "png", "webp"], accept_multiple_files=True, key="img_uploader")

# --- 3. EXECUTION BUTTON ---
if st.button("🚀 Process Images", type="primary", key="img_process_btn"):
    
    if not uploaded_files:
        st.warning("Please upload at least one image first!")
    elif not compress_enabled and not resize_enabled:
        st.warning("Please check at least one operation (Compress or Resize)!")
    else:
        st.subheader("Processing Images...")
        
        compressed_images_dict = {}
        cols = st.columns(3) 
        
        # --- 4. BATCH PROCESSING LOOP ---
        for index, uploaded_file in enumerate(uploaded_files):
            original_image = Image.open(uploaded_file)
            original_size_kb = uploaded_file.size / 1024
            img_format = original_image.format if original_image.format else "JPEG"
            
            if original_image.mode in ("RGBA", "P") and uploaded_file.name.lower().endswith(('jpg', 'jpeg')):
                original_image = original_image.convert("RGB")

            image_to_process = original_image.copy()

            # OPERATION 1: RESIZE (Only runs if checked)
            if resize_enabled:
                image_to_process.thumbnail((new_width, new_height), Image.Resampling.LANCZOS)

            buffer = io.BytesIO()

            # OPERATION 2: COMPRESS (Only runs if checked)
            if compress_enabled:
                current_quality = 95
                scale = 1.0
                
                image_to_process.save(buffer, format=img_format, quality=current_quality, optimize=True)
                while buffer.tell() / 1024 > target_kb and current_quality > 5:
                    current_quality -= 5
                    buffer = io.BytesIO()
                    image_to_process.save(buffer, format=img_format, quality=current_quality, optimize=True)
                    
                while buffer.tell() / 1024 > target_kb and scale > 0.1:
                    scale -= 0.1
                    shrink_w = int(image_to_process.width * scale)
                    shrink_h = int(image_to_process.height * scale)
                    if shrink_w < 10 or shrink_h < 10: break
                        
                    shrunk_img = image_to_process.resize((shrink_w, shrink_h), Image.Resampling.LANCZOS)
                    buffer = io.BytesIO()
                    shrunk_img.save(buffer, format=img_format, quality=10, optimize=True)
            
            # IF ONLY RESIZING: Save with high quality
            else:
                image_to_process.save(buffer, format=img_format, quality=95, optimize=True)

            # Save results
            compressed_size_kb = buffer.tell() / 1024
            compressed_images_dict[uploaded_file.name] = (buffer.getvalue(), img_format)
            
            # Display results
            with cols[index % 3]:
                st.image(buffer.getvalue(), use_container_width=True)
                st.caption(f"**{uploaded_file.name}**")
                st.text(f"Original: {original_size_kb:.1f} KB\nNew: {compressed_size_kb:.1f} KB")

        # --- 5. DOWNLOAD OPTIONS ---
        st.markdown("---")
        
        if len(compressed_images_dict) == 1:
            filename = list(compressed_images_dict.keys())[0]
            file_data, file_format = compressed_images_dict[filename]
            st.download_button(
                label="📥 Download Image",
                data=file_data,
                file_name=f"processed_{filename}",
                mime=f"image/{file_format.lower()}",
                key="img_dl_single"
            )
        
        elif len(compressed_images_dict) > 1:
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
                for file_name, (file_data, _) in compressed_images_dict.items():
                    zip_file.writestr(f"processed_{file_name}", file_data)
            
            st.success(f"Successfully processed {len(uploaded_files)} images!")
            st.download_button(
                label="📦 Download All as ZIP",
                data=zip_buffer.getvalue(),
                file_name="processed_images.zip",
                mime="application/zip",
                key="img_dl_zip"
            )