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
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()
    return pages_text


def extract_certificates_from_text(full_text, user_email):
    from app.extractor_agent import get_client

    prompt = (
        "The text below may contain ONE OR MORE certificates concatenated together "
        "(e.g. from a merged PDF). Identify EVERY distinct certificate present and "
        "extract its details. Return ONLY a JSON object with this exact shape, no "
        "preamble, no markdown:\n"
        '{"certificates": [{"certificate_name": "", "issuer": "", "date": "", '
        '"candidate_name": "", "is_valid_certificate": true, "trust_score": "verified"}]}\n'
        "trust_score must be one of: verified, unverified, suspicious.\n"
        "Set trust_score to suspicious if candidate_name does not plausibly match the account holder.\n"
        "Account holder email: " + user_email + "\n"
        'If you cannot find any certificate, return {"certificates": []}.\n'
        "Text:\n" + full_text[:12000]
    )

    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=3000,
    )
    parsed = json.loads(response.choices[0].message.content)
    certs = parsed.get("certificates", [])
    if isinstance(certs, dict):
        certs = [certs]
    return certs


def cert_fingerprint(cert):
    key = (
        str(cert.get("certificate_name", "")).strip().lower()
        + "|"
        + str(cert.get("issuer", "")).strip().lower()
        + "|"
        + str(cert.get("date", "")).strip().lower()
        + "|"
        + str(cert.get("candidate_name", "")).strip().lower()
    )
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


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

    pages_text = []
    if mime == "application/pdf":
        pages_text = extract_text_from_pdf(contents)
    full_text = "\n".join(pages_text)

    extracted_certs = []
    if full_text.strip():
        try:
            extracted_certs = extract_certificates_from_text(full_text, current_user)
        except Exception as e:
            print("Certificate extraction failed: " + str(e))
            extracted_certs = []

    if not extracted_certs:
        extracted_certs = [{
            "is_valid_certificate": None,
            "trust_score": "unverified",
            "certificate_name": None,
            "issuer": None,
            "date": None,
            "candidate_name": None,
        }]

    vault = knowledge_vault.find_one({"user_id": current_user}) or {}
    existing_fps = {c.get("fingerprint") for c in vault.get("certifications", []) if c.get("fingerprint")}

    added = []
    skipped_duplicates = 0

    for cert_data in extracted_certs:
        fp = cert_fingerprint(cert_data)
        if fp in existing_fps:
            skipped_duplicates += 1
            continue
        existing_fps.add(fp)

        cert_record = dict(cert_data)
        cert_record["fingerprint"] = fp
        cert_record["filename"] = file.filename
        cert_record["file_hash"] = file_hash
        cert_record["uploaded_at"] = datetime.utcnow()
        added.append(cert_record)

    if added:
        knowledge_vault.update_one(
            {"user_id": current_user},
            {
                "$push": {"certifications": {"$each": added}},
                "$set": {"updated_at": datetime.utcnow()},
                "$setOnInsert": {"created_at": datetime.utcnow()},
            },
            upsert=True,
        )

    return {
        "status": "uploaded",
        "added_count": len(added),
        "skipped_duplicates": skipped_duplicates,
        "certificates": added,
    }


@router.get("/api/vault")
async def get_vault(current_user: str = Depends(get_current_user)):
    vault = knowledge_vault.find_one({"user_id": current_user})
    if not vault:
        return {"user_id": current_user, "certifications": [], "projects": [], "skills": []}
    vault["_id"] = str(vault["_id"])
    return vault