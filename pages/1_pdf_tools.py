import streamlit as st
import io
import fitz  # PyMuPDF
import img2pdf
from pypdf import PdfReader, PdfWriter
import docx2txt
import pikepdf
import pytesseract
from pdf2image import convert_from_bytes
import base64

from sidebar import show_sidebar
show_sidebar()

st.set_page_config(page_title="PDF Tools", page_icon="📄", layout="wide")

st.title("📄 PDF Tools")
st.write("Merge, compress, split, convert, and secure your documents.")

# --- Helper: Human Readable Size ---
def get_file_size(file_bytes):
    size = len(file_bytes)
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024: return f"{size:.2f} {unit}"
        size /= 1024
    return f"{size:.2f} GB"

# --- Session State Initialization ---
if "staged_images" not in st.session_state:
    st.session_state.staged_images = []
if "uploaded_names" not in st.session_state:
    st.session_state.uploaded_names = set()

# --- Organize PDF tools into internal tabs ---
pdf_tabs = st.tabs(["⚡ Standard Tools", "👁️ Visual Organizer", "🔒 Security", "🔍 OCR & Repair"])

# ==========================================
# TAB 1: STANDARD TOOLS
# ==========================================
with pdf_tabs[0]:
    col_tools = st.tabs(["Merge", "JPG ↔ PDF", "Compress", "Word to PDF"])
    
    with col_tools[0]:
        st.header("Quick Merge")
        m_files = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True, key="quick_m")
        if m_files and st.button("Combine All", key="btn_m"):
            writer = PdfWriter()
            for f in m_files: writer.append(f)
            out = io.BytesIO()
            writer.write(out)
            final = out.getvalue()
            st.metric("Merged Size", get_file_size(final))
            st.download_button("Download Merged PDF", final, "merged.pdf")

    with col_tools[1]:
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("JPG to PDF")
            imgs = st.file_uploader("Upload Images (Sequential)", type=["jpg", "jpeg", "png"], accept_multiple_files=True, key="img2pdf_up")
            if imgs:
                for img in imgs:
                    if img.name not in st.session_state.uploaded_names:
                        st.session_state.staged_images.append(img.getvalue())
                        st.session_state.uploaded_names.add(img.name)
            
            if st.session_state.staged_images:
                st.write(f"Images staged: {len(st.session_state.staged_images)}")
            
            col_a, col_b = st.columns(2)
            with col_a:
                if st.session_state.staged_images and st.button("Convert to PDF"):
                    pdf_b = img2pdf.convert(st.session_state.staged_images)
                    st.metric("New PDF Size", get_file_size(pdf_b))
                    st.download_button("Download PDF", pdf_b, "images.pdf")
            with col_b:
                if st.session_state.staged_images and st.button("Clear Selection"):
                    st.session_state.staged_images = []
                    st.session_state.uploaded_names = set()
                    st.rerun()

        with c2:
            st.subheader("PDF to JPG")
            p2j_file = st.file_uploader("Upload PDF", type="pdf", key="p2j")
            if p2j_file and st.button("Extract Pages"):
                doc = fitz.open(stream=p2j_file.read(), filetype="pdf")
                for i, page in enumerate(doc):
                    pix = page.get_pixmap()
                    img_d = pix.tobytes("jpg")
                    st.download_button(f"Download Page {i+1} ({get_file_size(img_d)})", img_d, f"page_{i+1}.jpg", key=f"dl_p2j_{i}")

    with col_tools[2]:
        st.header("Lossless Compressor")
        comp_file = st.file_uploader("Upload heavy PDF", type="pdf", key="comp")
        if comp_file and st.button("Optimize"):
            orig = comp_file.getvalue()
            reader = PdfReader(io.BytesIO(orig))
            writer = PdfWriter()
            for p in reader.pages: 
                p.compress_content_streams()
                writer.add_page(p)
            out = io.BytesIO()
            writer.write(out)
            new_b = out.getvalue()
            diff = ((len(orig)-len(new_b))/len(orig))*100
            st.metric("Compressed Size", get_file_size(new_b), delta=f"-{diff:.1f}%")
            st.download_button("Download Optimized PDF", new_b, "compressed.pdf")

    with col_tools[3]:
        st.header("Word to PDF")
        w_file = st.file_uploader("Upload .docx", type="docx")
        if w_file and st.button("Convert Word"):
            text = docx2txt.process(w_file)
            new_p = fitz.open()
            pg = new_p.new_page()
            pg.insert_text((50, 72), text)
            out = io.BytesIO()
            new_p.save(out)
            st.download_button("Download PDF", out.getvalue(), "word_doc.pdf")

# ==========================================
# TAB 2: VISUAL ORGANIZER
# ==========================================
with pdf_tabs[1]:
    st.header("Visual Page Reorder")
    v_file = st.file_uploader("Upload PDF to Sort", type="pdf", key="vis_sort")
    if v_file:
        doc_v = fitz.open(stream=v_file.read(), filetype="pdf")
        st.write("Select pages in the order you want them to appear:")
        selected_pages = []
        cols = st.columns(5)
        for i in range(len(doc_v)):
            page = doc_v[i]
            pix = page.get_pixmap(matrix=fitz.Matrix(0.2, 0.2))
            b64 = base64.b64encode(pix.tobytes("png")).decode()
            with cols[i % 5]:
                st.image(f"data:image/png;base64,{b64}", caption=f"Pg {i+1}")
                if st.checkbox(f"Add {i+1}", key=f"v_{i}"):
                    selected_pages.append(i)
        
        if selected_pages and st.button("Create Reordered PDF"):
            writer_v = PdfWriter()
            reader_v = PdfReader(io.BytesIO(v_file.getvalue()))
            for p_num in selected_pages: 
                writer_v.add_page(reader_v.pages[p_num])
            out_v = io.BytesIO()
            writer_v.write(out_v)
            st.download_button("Download Reordered PDF", out_v.getvalue(), "reordered.pdf")

# ==========================================
# TAB 3: SECURITY
# ==========================================
with pdf_tabs[2]:
    st.header("Password Security")
    sec_mode = st.radio("Action", ["Lock (Add Password)", "Unlock (Remove Password)"])
    s_file = st.file_uploader("Upload PDF", type="pdf", key="sec_upload")
    if s_file:
        upass = st.text_input("Password", type="password")
        if st.button("Execute Security"):
            try:
                if sec_mode == "Lock (Add Password)":
                    with pikepdf.open(s_file) as pdf:
                        out_s = io.BytesIO()
                        enc = pikepdf.Encryption(user=upass, owner=upass)
                        pdf.save(out_s, encryption=enc)
                        st.download_button("Download Locked PDF", out_s.getvalue(), "locked.pdf")
                else:
                    with pikepdf.open(s_file, password=upass) as pdf:
                        out_s = io.BytesIO()
                        pdf.save(out_s)
                        st.download_button("Download Unlocked PDF", out_s.getvalue(), "unlocked.pdf")
            except Exception as e: 
                st.error(f"Error: {e}")

# ==========================================
# TAB 4: OCR & REPAIR
# ==========================================
with pdf_tabs[3]:
    col_ocr, col_rep = st.columns(2)
    with col_ocr:
        st.header("OCR (Image to Text)")
        o_file = st.file_uploader("Upload Scanned PDF", type="pdf", key="ocr_up")
        o_lang = st.selectbox("Language", ["eng", "hin", "eng+hin"])
        if o_file and st.button("Extract Text"):
            with st.spinner("Analyzing..."):
                imgs_o = convert_from_bytes(o_file.read())
                res = ""
                for i, img in enumerate(imgs_o):
                    res += f"\n--- Page {i+1} ---\n" + pytesseract.image_to_string(img, lang=o_lang)
                st.text_area("Result", res, height=250)
                st.download_button("Download TXT", res, "extracted.txt")
                
    with col_rep:
        st.header("Repair PDF")
        r_file = st.file_uploader("Upload Broken PDF", type="pdf", key="rep_up")
        if r_file and st.button("Fix PDF Structure"):
            try:
                with pikepdf.open(r_file) as pdf_r:
                    out_r = io.BytesIO()
                    pdf_r.save(out_r)
                    st.success("Rebuilt successfully!")
                    st.download_button("Download Fixed PDF", out_r.getvalue(), "fixed.pdf")
            except: 
                st.error("Corruption too severe for automated repair.")