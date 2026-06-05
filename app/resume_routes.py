from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from app.auth_routes import get_current_user
from app.extractor_agent import get_client
import json
import io

router = APIRouter()

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    try:
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""
        return text.strip()
    except Exception as e:
        print(f"PDF extraction error: {e}")
        return ""

@router.post("/api/resume/analyze")
async def analyze_resume(
    resume: UploadFile = File(...),
    jd: str = Form(...),
    current_user: str = Depends(get_current_user)
):
    if not resume.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF resumes supported")
    if len(jd.strip()) < 50:
        raise HTTPException(status_code=400, detail="Job description too short")

    pdf_bytes = await resume.read()
    if len(pdf_bytes) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Resume too large (max 5MB)")

    resume_text = extract_text_from_pdf(pdf_bytes)
    if not resume_text or len(resume_text) < 100:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

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

Be specific. Extract at least 5 missing keywords, 3 weak sections with fixes, and 3 rewritten bullets.
Return ONLY the JSON. No explanation."""

    client = get_client()
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            response_format={"type": "json_object"},
            max_tokens=2000
        )
        raw = response.choices[0].message.content.strip()
        result = json.loads(raw)
        return result
    except json.JSONDecodeError as e:
        print(f"Resume analysis parse error: {e}")
        raise HTTPException(status_code=500, detail="AI response parsing failed")
    except Exception as e:
        print(f"Resume analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")
