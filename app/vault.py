import hashlib
import json
import re
from datetime import date, datetime

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile

from app.auth_routes import get_current_user
from app.database import knowledge_vault, upload_logs

router = APIRouter()

MAX_FILE_SIZE = 5 * 1024 * 1024
DAILY_PDF_LIMIT = 2
ALLOWED_MIME_TYPES = {"application/pdf", "image/jpeg", "image/png"}
MAX_PAGES = 60  # hard safety cap so an absurd upload can't run away


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
    pages_text = [page.get_text() for page in doc]
    doc.close()
    return pages_text


def extract_certificate_from_page(page_text, user_email):
    """One AI call per page. Each certificate is almost always exactly one page,
    so this maximizes recall — a single call never has to juggle multiple certs."""
    from app.extractor_agent import get_client

    prompt = (
        "The text below is ONE PAGE from a document. It may contain exactly one "
        "certificate, or it may contain no certificate at all (e.g. a cover page or "
        "blank separator). Extract the certificate details if present. Return ONLY a "
        "JSON object with this exact shape, no preamble, no markdown:\n"
        '{"found": true, "certificate_name": "", "issuer": "", "date": "", '
        '"candidate_name": "", "is_valid_certificate": true, "trust_score": "verified"}\n'
        "trust_score must be one of: verified, unverified, suspicious.\n"
        "Set trust_score to suspicious if candidate_name does not plausibly match the account holder.\n"
        "Account holder email: " + user_email + "\n"
        'If this page does NOT contain a certificate, return {"found": false}.\n'
        "Page text:\n" + page_text[:4000]
    )

    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        max_tokens=500,
    )
    parsed = json.loads(response.choices[0].message.content)
    if not parsed.get("found"):
        return None
    parsed.pop("found", None)
    return parsed


def normalize_for_fingerprint(value):
    s = str(value or "").strip().lower()
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def content_fingerprint(cert):
    """Catches the SAME certificate appearing across DIFFERENT uploaded files
    (e.g. a standalone PDF and again inside a big merged PDF). Normalized +
    collapsed so minor AI phrasing differences between calls don't break matching."""
    key = "|".join([
        normalize_for_fingerprint(cert.get("certificate_name")),
        normalize_for_fingerprint(cert.get("issuer")),
        normalize_for_fingerprint(cert.get("date")),
        normalize_for_fingerprint(cert.get("candidate_name")),
    ])
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


def page_fingerprint(file_hash, page_index):
    """Stable regardless of how the AI phrases its output. Re-uploading the exact
    same file always reproduces these exact fingerprints, so a true duplicate
    re-upload of the same file is always blocked deterministically."""
    key = file_hash + "|page|" + str(page_index)
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
        raise HTTPException(400, "This exact file has already been uploaded.")

    upload_logs.update_one(
        {"user_id": current_user, "date": today},
        {"$inc": {"pdf_count": 1}, "$push": {"hashes": file_hash}},
        upsert=True,
    )

    pages_text = []
    if mime == "application/pdf":
        pages_text = extract_text_from_pdf(contents)

    for idx, pt in enumerate(pages_text):
        print("DEBUG page " + str(idx) + " len=" + str(len(pt.strip())) + " preview=" + repr(pt.strip()[:80]))

    if len(pages_text) > MAX_PAGES:
        raise HTTPException(400, "Too many pages (" + str(len(pages_text)) + "). Max " + str(MAX_PAGES) + " pages per upload.")

    vault = knowledge_vault.find_one({"user_id": current_user}) or {}
    existing_certs = vault.get("certifications", [])
    existing_page_fps = {c.get("page_fingerprint") for c in existing_certs if c.get("page_fingerprint")}
    existing_content_fps = {c.get("content_fingerprint") for c in existing_certs if c.get("content_fingerprint")}

    added = []
    skipped_duplicates = 0
    skipped_empty_pages = 0
    failed_pages = []

    for idx, page_text in enumerate(pages_text):
        if not page_text.strip():
            skipped_empty_pages += 1
            continue

        pfp = page_fingerprint(file_hash, idx)
        if pfp in existing_page_fps:
            skipped_duplicates += 1
            continue

        try:
            cert_data = extract_certificate_from_page(page_text, current_user)
        except Exception as e:
            print("Page " + str(idx) + " extraction failed: " + str(e))
            failed_pages.append(idx)
            continue

        if cert_data is None:
            continue

        cfp = content_fingerprint(cert_data)
        if cfp in existing_content_fps:
            skipped_duplicates += 1
            existing_page_fps.add(pfp)
            continue

        cert_record = dict(cert_data)
        cert_record["page_fingerprint"] = pfp
        cert_record["content_fingerprint"] = cfp
        cert_record["page_index"] = idx
        cert_record["filename"] = file.filename
        cert_record["file_hash"] = file_hash
        cert_record["uploaded_at"] = datetime.utcnow()

        existing_page_fps.add(pfp)
        existing_content_fps.add(cfp)
        added.append(cert_record)

    if not pages_text:
        added.append({
            "is_valid_certificate": None,
            "trust_score": "unverified",
            "certificate_name": None,
            "issuer": None,
            "date": None,
            "candidate_name": None,
            "page_fingerprint": page_fingerprint(file_hash, 0),
            "content_fingerprint": content_fingerprint({}),
            "filename": file.filename,
            "file_hash": file_hash,
            "uploaded_at": datetime.utcnow(),
        })

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
        "pages_processed": len(pages_text),
        "added_count": len(added),
        "skipped_duplicates": skipped_duplicates,
        "skipped_empty_pages": skipped_empty_pages,
        "failed_pages": failed_pages,
        "certificates": added,
    }


@router.get("/api/vault")
async def get_vault(current_user: str = Depends(get_current_user)):
    vault = knowledge_vault.find_one({"user_id": current_user})
    if not vault:
        return {"user_id": current_user, "certifications": [], "projects": [], "skills": []}
    vault["_id"] = str(vault["_id"])
    return vault