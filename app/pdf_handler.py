import fitz  # PyMuPDF
import requests
import os
import tempfile


def download_and_extract_pdf(media_url: str) -> str:
    """Download PDF from Meta URL and extract text"""
    token = os.getenv("WHATSAPP_TOKEN")
    headers = {"Authorization": f"Bearer {token}"}

    # Step 1: Get the actual download URL from Meta
    media_response = requests.get(media_url, headers=headers)
    if media_response.status_code != 200:
        print(f"Failed to get media info: {media_response.status_code}")
        return None

    download_url = media_response.json().get("url")
    if not download_url:
        print("No download URL in media response")
        return None

    # Step 2: Download the PDF
    pdf_response = requests.get(download_url, headers=headers)
    if pdf_response.status_code != 200:
        print(f"Failed to download PDF: {pdf_response.status_code}")
        return None

    # Step 3: Save to temp file and extract text
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
        tmp.write(pdf_response.content)
        tmp_path = tmp.name

    try:
        doc = fitz.open(tmp_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        print(f"Extracted {len(text)} characters from PDF")
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return None
    finally:
        os.unlink(tmp_path)