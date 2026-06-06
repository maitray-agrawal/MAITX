from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.auth_routes import get_current_user
from app.extractor_agent import get_client
from app.database import (
    resumes_collection, jobs_collection,
    save_resume_to_gridfs, get_resume_from_gridfs, delete_resume_from_gridfs
)
from bson import ObjectId
from datetime import datetime
import json
import fitz

router = APIRouter()

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

def run_ats_analysis(resume_text: str, jd: str) -> dict:
    prompt = f"""You are an expert resume coach and ATS specialist. Analyze this resume against the job description.

RESUME:
{resume_text[:4000]}

JOB DESCRIPTION:
{jd[:2000]}

Return ONLY a valid JSON object with exactly this structure:
{{
  "match_score": <integer 0-100>,
  "score_breakdown": {{
    "skills_match": <integer 0-100>,
    "experience_match": <integer 0-100>,
    "education_match": <integer 0-100>,
    "keywords_match": <integer 0-100>
  }},
  "summary": "<2-3 sentence overall assessment>",
  "matched_keywords": ["keyword1", "keyword2"],
  "missing_keywords": ["keyword1", "keyword2"],
  "strong_sections": ["section1", "section2"],
  "weak_sections": [
    {{"section": "section name", "issue": "what is weak", "fix": "how to improve it"}}
  ],
  "rewritten_bullets": [
    {{"original": "original bullet point", "improved": "improved version with metrics and keywords"}}
  ],
  "ats_tips": ["tip1", "tip2", "tip3"]
}}
Return ONLY the JSON. No explanation."""
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        response_format={"type": "json_object"},
        max_tokens=2000
    )
    return json.loads(response.choices[0].message.content.strip())

# Upload resume
@router.post("/api/resume/upload")
async def upload_resume(
    resume: UploadFile = File(...),
    name: str = Form(...),
    set_active: bool = Form(False),
    current_user: str = Depends(get_current_user)
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes supported")
    pdf_bytes = await resume.read()
    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Resume too large (max 5MB)")
    resume_text = extract_text_from_pdf(pdf_bytes)
    if not resume_text or len(resume_text) < 50:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    file_id = save_resume_to_gridfs(pdf_bytes, resume.filename, current_user)

    if set_active:
        resumes_collection.update_many({"user_id": current_user}, {"$set": {"active": False}})

    doc = {
        "user_id": current_user,
        "name": name,
        "filename": resume.filename,
        "gridfs_id": file_id,
        "active": set_active,
        "uploaded_at": datetime.utcnow(),
        "text_preview": resume_text[:500]
    }
    result = resumes_collection.insert_one(doc)
    return {"id": str(result.inserted_id), "name": name, "active": set_active}

# List resumes
@router.get("/api/resume/list")
async def list_resumes(current_user: str = Depends(get_current_user)):
    resumes = list(resumes_collection.find({"user_id": current_user}).sort("uploaded_at", -1))
    for r in resumes:
        r["id"] = str(r.pop("_id"))
        r.pop("gridfs_id", None)
        r.pop("text_preview", None)
        if r.get("uploaded_at"):
            r["uploaded_at"] = r["uploaded_at"].isoformat()
    return resumes

# Set active resume
@router.post("/api/resume/set-active/{resume_id}")
async def set_active_resume(resume_id: str, current_user: str = Depends(get_current_user)):
    resumes_collection.update_many({"user_id": current_user}, {"$set": {"active": False}})
    resumes_collection.update_one(
        {"_id": ObjectId(resume_id), "user_id": current_user},
        {"$set": {"active": True}}
    )
    return {"status": "updated"}

# Delete resume
@router.delete("/api/resume/{resume_id}")
async def delete_resume(resume_id: str, current_user: str = Depends(get_current_user)):
    doc = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": current_user})
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    delete_resume_from_gridfs(doc["gridfs_id"])
    resumes_collection.delete_one({"_id": ObjectId(resume_id)})
    return {"status": "deleted"}

# Manual analyze (existing flow but uses saved resume if no file uploaded)
@router.post("/api/resume/analyze")
async def analyze_resume(
    resume: UploadFile = File(None),
    resume_id: str = Form(None),
    jd: str = Form(...),
    current_user: str = Depends(get_current_user)
):
    if len(jd.strip()) < 3:
        raise HTTPException(status_code=400, detail="Enter at least a role or keywords")

    if resume and resume.filename:
        pdf_bytes = await resume.read()
        resume_text = extract_text_from_pdf(pdf_bytes)
    elif resume_id:
        doc = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": current_user})
        if not doc:
            raise HTTPException(status_code=404, detail="Resume not found")
        pdf_bytes = get_resume_from_gridfs(doc["gridfs_id"])
        resume_text = extract_text_from_pdf(pdf_bytes)
    else:
        # Use active resume
        doc = resumes_collection.find_one({"user_id": current_user, "active": True})
        if not doc:
            raise HTTPException(status_code=400, detail="No resume uploaded. Upload a resume first.")
        pdf_bytes = get_resume_from_gridfs(doc["gridfs_id"])
        resume_text = extract_text_from_pdf(pdf_bytes)

    if not resume_text or len(resume_text) < 50:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    try:
        result = run_ats_analysis(resume_text, jd)
        return result
    except Exception as e:
        print(f"Resume analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# Auto-analyze a specific job against active resume
@router.post("/api/resume/analyze-job/{job_id}")
async def analyze_job(job_id: str, current_user: str = Depends(get_current_user)):
    job = jobs_collection.find_one({"_id": ObjectId(job_id), "user_id": current_user})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    active_resume = resumes_collection.find_one({"user_id": current_user, "active": True})
    if not active_resume:
        raise HTTPException(status_code=400, detail="No active resume. Upload and set a resume as active first.")

    pdf_bytes = get_resume_from_gridfs(active_resume["gridfs_id"])
    resume_text = extract_text_from_pdf(pdf_bytes)

    jd = f"{job.get('company_name', '')} {job.get('role', '')} {job.get('eligibility', '')} {job.get('extra_notes', '')}"

    try:
        result = run_ats_analysis(resume_text, jd)
        jobs_collection.update_one(
            {"_id": ObjectId(job_id)},
            {"$set": {"ats_score": result["match_score"], "ats_analysis": result}}
        )
        return result
    except Exception as e:
        print(f"Auto ATS error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
