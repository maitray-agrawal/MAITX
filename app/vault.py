import hashlib
import json
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth_routes import get_current_user
from app.database import knowledge_vault, upload_logs

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024
DAILY_PDF_LIMIT = 2
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}


def detect_mime(contents, filename):
    try:
        import magic
        return magic.from_buffer(contents, mime=True)
    except Exception:
        if contents.startswith(b"%PDF"):
            return "application/pdf"
        if contents.startswith(b"\xff\xd8\xff"):
            return "image/jpeg"
        if contents.startswith(b"\x89PNG\r\n\x1a\n"):
            return "image/png"
        ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
        print("WARNING: could not detect MIME for " + filename + ", falling back to extension " + ext)
        fallback = {"pdf": "application/pdf", "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png"}
        return fallback.get(ext, "application/octet-stream")


def extract_text_from_pdf(contents):
    import fitz
    doc = fitz.open(stream=contents, filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    doc.close()
    return text


def extract_certificate_details(text, user_email):
    from app.extractor_agent import get_client

    prompt = "Extract certificate details from this text and return ONLY JSON, no preamble, no markdown:\n"
    prompt += "{\"certificate_name\": \"\", \"issuer\": \"\", \"date\": \"\", \"candidate_name\": \"\", \"is_valid_certificate\": true, \"trust_score\": \"verified\"}\n"
    prompt += "trust_score must be one of: verified, unverified, suspicious.\n"
    prompt += "Set trust_score to suspicious if candidate_name does not plausibly match the account holder.\n"
    prompt += "Account holder email: " + user_email + "\n"
    prompt += "Text:\n" + text[:3000]

    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
    )
    return json.loads(response.choices[0].message.content)


@router.post("/api/vault/upload-certificate")
async def upload_certificate(file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    contents = await file.read()

    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(400, "File too large. Max 5MB allowed.")

    mime = detect_mime(contents, file.filename or "")
    if mime not in ALLOWED_MIME_TYPES:
        raise HTTPException(400, "Invalid file type: " + mime + ". Only PDF, JPG, PNG allowed.")

    today = str(date.today())
    log = upload_logs.find_one({"user_id": current_user, "date": today})
    if log and log.get("pdf_count", 0) >= DAILY_PDF_LIMIT:
        raise HTTPException(429, "Daily limit reached. Max " + str(DAILY_PDF_LIMIT) + " uploads per day. Please combine all certificates into one PDF.")

    file_hash = hashlib.sha256(contents).hexdigest()
    if log and file_hash in log.get("hashes", []):
        raise HTTPException(400, "This file has already been uploaded.")

    upload_logs.update_one(
        {"user_id": current_user, "date": today},
        {"$inc": {"pdf_count": 1}, "$push": {"hashes": file_hash}},
        upsert=True,
    )

    text = ""
    if mime == "application/pdf":
        text = extract_text_from_pdf(contents)

    cert_data = {}
    if text.strip():
        try:
            cert_data = extract_certificate_details(text, current_user)
        except Exception as e:
            print("Certificate extraction failed: " + str(e))
            cert_data = {"is_valid_certificate": None, "trust_score": "unverified", "error": str(e)}

    cert_record = dict(cert_data)
    cert_record["filename"] = file.filename
    cert_record["file_hash"] = file_hash
    cert_record["uploaded_at"] = datetime.utcnow()

    knowledge_vault.update_one(
        {"user_id": current_user},
        {
            "$push": {"certifications": cert_record},
            "$set": {"updated_at": datetime.utcnow()},
            "$setOnInsert": {"created_at": datetime.utcnow()},
        },
        upsert=True,
    )

    return {"status": "uploaded", "certificate": cert_record}


@router.get("/api/vault")
async def get_vault(current_user: str = Depends(get_current_user)):
    vault = knowledge_vault.find_one({"user_id": current_user})
    if not vault:
        return {"user_id": current_user, "certifications": [], "projects": [], "skills": []}
    vault["_id"] = str(vault["_id"])
    return vault
