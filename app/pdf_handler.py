content = """import fitz  # PyMuPDF for PDF
import requests
import os
import tempfile


def extract_text_from_pdf(file_path: str) -> str:
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text.strip()


def extract_text_from_docx(file_path: str) -> str:
    from docx import Document
    doc = Document(file_path)
    text = ""
    for para in doc.paragraphs:
        text += para.text + "\\n"
    return text.strip()


def download_and_extract_pdf(media_url: str, mime_type: str = "application/pdf") -> str:
    token = os.getenv("WHATSAPP_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Get download URL from Meta
    media_response = requests.get(media_url, headers=headers)
    if media_response.status_code != 200:
        print(f"Failed to get media info: {media_response.status_code}")
        return None

    download_url = media_response.json().get("url")
    if not download_url:
        print("No download URL in media response")
        return None

    # Step 2: Download the file
    file_response = requests.get(download_url, headers=headers)
    if file_response.status_code != 200:
        print(f"Failed to download file: {file_response.status_code}")
        return None

    # Step 3: Determine file type and extract text
    is_docx = "word" in mime_type.lower() or "docx" in mime_type.lower()
    suffix = ".docx" if is_docx else ".pdf"

    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_response.content)
        tmp_path = tmp.name

    try:
        if is_docx:
            text = extract_text_from_docx(tmp_path)
            print(f"Extracted {len(text)} characters from DOCX")
        else:
            text = extract_text_from_pdf(tmp_path)
            print(f"Extracted {len(text)} characters from PDF")
        return text
    except Exception as e:
        print(f"File extraction error: {e}")
        return None
    finally:
        os.unlink(tmp_path)
"""

with open("app/pdf_handler.py", "w", encoding="utf-8") as f:
    f.write(content)
print("pdf_handler.py updated with DOCX support")