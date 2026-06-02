# 🛠️ Universal Utility Suite (Lite tools) 

A fast, lightweight, and serverless web application built with Python and Streamlit. This universal suite combines powerful PDF manipulation tools and smart image processing utilities into a single, easy-to-use platform. 

**Privacy First:** This tool processes everything entirely in your server's RAM. Your files are never permanently saved to a hard drive, ensuring maximum security and privacy for your sensitive documents and images.

---

## ✨ Features

### 📄 PDF Tools
* **Quick Merge:** Concatenate multiple PDF documents into one in seconds.
* **JPG ↔ PDF:** Two-way conversion between sequential images and PDF documents.
* **PDF Compressor:** Lossless compression to reduce file size for email and web uploads.
* **Word to PDF:** Extract and convert `.docx` content into a portable PDF format.
* **Visual Organizer:** See previews of your pages and easily rearrange them into a new document.
* **Security & Passwords:** Easily lock (encrypt) or unlock (decrypt) PDF files.
* **OCR & Repair:** Extract text from scanned PDFs using Tesseract OCR, or rebuild broken/corrupted PDF file structures.

### 🖼️ Image Tools
* **Batch Processing:** Upload and process multiple images at the same time (up to 10 recommended).
* **Target Size Compression:** Specify an exact target size (e.g., 50 KB), and the app will intelligently lower the quality and scale down the image until it fits the requirement.
* **Smart Resizing:** Set maximum pixel dimensions. The app uses `Lanczos` resampling and maintains the original aspect ratio so your images never stretch or distort.
* **Bulk Download:** Download single files normally, or automatically package multiple processed images into a `.zip` file for 1-click downloading.

---

## 📦 Tech Stack

* **Frontend/UI:** [Streamlit](https://streamlit.io/)
* **PDF Logic:** `pypdf`, `PyMuPDF` (fitz), `pikepdf`
* **Image Conversion & Processing:** `img2pdf`, `Pillow` (PIL), `pdf2image`
* **Document Parsing:** `docx2txt`
* **Optical Character Recognition (OCR):** `pytesseract`

---

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/Hexton09/PDF-Lite.git](https://github.com/Hexton09/PDF-Lite.git)
cd PDF-Lite
```

Windows
```
python -m venv venv
venv\Scripts\activate
```
Mac/linux
```
python3 -m venv venv
source venv/bin/activate
```

Dependencies
```
pip install -r requirements.txt
```

Start the app
```
streamlit run app.py
```
