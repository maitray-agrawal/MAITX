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
        raise HTTPException(status_code=400, detail="Could not extract text from resume PDF")

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
    if len(jd.strip()) < 2:
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
        raise HTTPException(status_code=400, detail="Could not extract text from resume PDF")

    try:
        result = run_ats_analysis(resume_text, jd)
        return result
    except Exception as e:
        print(f"Resume analysis error: {e}")
        raise HTTPException(status_code=500, detail="Analysis failed")

# Download resume PDF
@router.get("/api/resume/download/{resume_id}")
async def download_resume(resume_id: str, current_user: str = Depends(get_current_user)):
    from fastapi.responses import Response
    doc = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": current_user})
    if not doc:
        raise HTTPException(status_code=404, detail="Resume not found")
    pdf_bytes = get_resume_from_gridfs(doc["gridfs_id"])
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={doc['filename']}"}
    )

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

# Tailor resume for a specific job
@router.post("/api/resume/tailor/{job_id}")
async def tailor_resume(job_id: str, style: str = Form("ats"), current_user: str = Depends(get_current_user)):
    from fastapi.responses import Response
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
    from reportlab.lib.enums import TA_LEFT, TA_CENTER
    import io

    job = jobs_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    active_resume = resumes_collection.find_one({"user_id": current_user, "active": True})
    if not active_resume:
        raise HTTPException(status_code=400, detail="No active resume. Upload and set a resume as active first.")

    pdf_bytes = get_resume_from_gridfs(active_resume["gridfs_id"])
    resume_text = extract_text_from_pdf(pdf_bytes)

    jd = f"{job.get('company_name','')} - {job.get('role','')}\n{job.get('eligibility','')}\n{job.get('extra_notes','')}"

    style_instruction = """Format as a clean ATS-optimized resume. Use simple section headers, no tables or columns. 
    Prioritize keywords from the job description. Use action verbs and quantify achievements.""" if style == "ats" else """Format as a professional visually appealing resume. 
    Keep the candidate's original structure but enhance content for the target role."""

    prompt = f"""You are a panel of four experts reviewing this resume simultaneously:
1. ATS SYSTEM: You scan for exact keyword matches, proper formatting, section headers, and parsability
2. SENIOR RECRUITER (10 years exp): You look for clear career progression, quantified achievements, and relevance to role
3. HIRING MANAGER: You assess technical depth, project impact, and cultural fit signals
4. INTERVIEW COACH: You ensure every bullet tells a story using STAR method with measurable outcomes

YOUR MISSION: Produce the strongest possible resume for this candidate for this specific job.

STRICT RULES — VIOLATION IS NOT ACCEPTABLE:
1. NEVER invent fake experience, companies, dates, or achievements
2. PRESERVE exact name, email, phone, university, CGPA, company names, job titles, dates
3. KEEP every single experience, internship, and project — removing any is forbidden
4. REWRITE every bullet point using: Action Verb + Task + Result + Metric format
5. INJECT job description keywords NATURALLY into bullets, summary, and skills
6. SKILLS section must have minimum 20 skills organized by category
7. SUMMARY must: mention exact job title, top 3 JD requirements, and candidate's strongest achievement
8. Every bullet must start with a strong action verb (Engineered, Architected, Optimized, Spearheaded, etc.)
9. Quantify EVERYTHING possible — use numbers already in resume, estimate where logical
10. Projects must highlight business impact, not just technical description
11. Fix any typos in contact info — double check email carefully character by character

ORIGINAL RESUME:
{resume_text[:4000]}

TARGET JOB:
{jd[:1000]}

STYLE: {style_instruction}

Return ONLY a JSON object with this exact structure:
{{
  "name": "candidate full name",
  "email": "email",
  "phone": "phone",
  "linkedin": "linkedin url or empty string",
  "summary": "2-3 sentence professional summary tailored to this role",
  "skills_by_category": {{
    "AI & Machine Learning": ["skill1", "skill2"],
    "Programming Languages": ["Python", "Java"],
    "Frameworks & Tools": ["FastAPI", "Django"],
    "Cloud & DevOps": ["AWS", "Docker"],
    "Data & Databases": ["MongoDB", "SQL"]
  }},
  "skills": ["flat list of ALL skills combined - minimum 20"],
  "experience": [
    {{
      "title": "job title",
      "company": "company name",
      "duration": "date range",
      "bullets": ["achievement 1 with metrics", "achievement 2"]
    }}
  ],
  "education": [
    {{
      "degree": "degree name",
      "institution": "university name",
      "year": "graduation year",
      "details": "CGPA or relevant details"
    }}
  ],
  "projects": [
    {{
      "name": "project name",
      "description": "2-3 line description tailored to job",
      "tech": "technologies used"
    }}
  ],
  "certifications": ["cert1", "cert2"]
}}
Return ONLY the JSON. No explanation."""

    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        response_format={"type": "json_object"},
        max_tokens=3000
    )

    import json
    data = json.loads(response.choices[0].message.content.strip())

    # Generate strict ATS-compliant PDF
    buffer = io.BytesIO()

    # ATS standard: 1 inch margins, no columns, no tables, no graphics
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2.0*cm, leftMargin=2.0*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm
    )
    story = []

    # ATS-safe styles: black text only, standard fonts, clear hierarchy
    name_style = ParagraphStyle("name",
        fontSize=16, fontName="Helvetica-Bold",
        textColor=colors.black,
        alignment=1,  # center
        spaceAfter=2, spaceBefore=0)

    contact_style = ParagraphStyle("contact",
        fontSize=10, fontName="Helvetica",
        textColor=colors.black,
        alignment=1,
        spaceAfter=6)

    section_style = ParagraphStyle("section",
        fontSize=11, fontName="Helvetica-Bold",
        textColor=colors.black,
        spaceBefore=10, spaceAfter=3,
        borderPadding=(0,0,2,0))

    role_style = ParagraphStyle("role",
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.black,
        spaceAfter=1, spaceBefore=4)

    date_style = ParagraphStyle("date",
        fontSize=10, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#444444"),
        spaceAfter=2)

    body_style = ParagraphStyle("body",
        fontSize=10, fontName="Helvetica",
        textColor=colors.black,
        spaceAfter=2, leading=14)

    bullet_style = ParagraphStyle("bullet",
        fontSize=10, fontName="Helvetica",
        textColor=colors.black,
        spaceAfter=2, leading=13,
        leftIndent=14)

    def section_header(title):
        story.append(Spacer(1, 4))
        story.append(Paragraph(title.upper(), section_style))
        # Simple black line - ATS safe
        story.append(HRFlowable(
            width="100%", thickness=1,
            color=colors.black,
            spaceAfter=4, spaceBefore=0
        ))

    # ── NAME (centered, bold) ──
    name = data.get("name", "").strip()
    story.append(Paragraph(name, name_style))

    # ── CONTACT LINE (single line, | separated - ATS standard) ──
    contact_parts = []
    if data.get("phone"): contact_parts.append(data["phone"].strip())
    if data.get("email"): contact_parts.append(data["email"].strip())
    if data.get("linkedin") and data["linkedin"].strip():
        contact_parts.append(data["linkedin"].strip())
    if contact_parts:
        story.append(Paragraph(" | ".join(contact_parts), contact_style))

    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.black, spaceAfter=6))

    # ── PROFESSIONAL SUMMARY ──
    if data.get("summary"):
        section_header("Professional Summary")
        story.append(Paragraph(data["summary"].strip(), body_style))

    # ── SKILLS (category: skill1, skill2 format - ATS parseable) ──
    section_header("Technical Skills")
    if data.get("skills_by_category"):
        for category, skills in data["skills_by_category"].items():
            if skills:
                skills_clean = [s.strip() for s in skills if s.strip()]
                story.append(Paragraph(
                    f"<b>{category}:</b> {', '.join(skills_clean)}",
                    body_style
                ))
    elif data.get("skills"):
        # Group into rows of 6 for readability
        skills = [s.strip() for s in data["skills"] if s.strip()]
        for i in range(0, len(skills), 6):
            story.append(Paragraph(", ".join(skills[i:i+6]), body_style))

    # ── EXPERIENCE ──
    if data.get("experience"):
        section_header("Professional Experience")
        for exp in data["experience"]:
            title = exp.get("title", "").strip()
            company = exp.get("company", "").strip()
            duration = exp.get("duration", "").strip()

            # Role + Company on one line, Date on next - ATS standard
            story.append(Paragraph(f"<b>{title}</b>, {company}", role_style))
            story.append(Paragraph(duration, date_style))

            for bullet in exp.get("bullets", []):
                bullet = bullet.strip()
                if bullet:
                    # Ensure bullet starts with action verb
                    story.append(Paragraph(f"•  {bullet}", bullet_style))
            story.append(Spacer(1, 4))

    # ── PROJECTS ──
    if data.get("projects"):
        section_header("Projects")
        for proj in data["projects"]:
            pname = proj.get("name", "").strip()
            desc = proj.get("description", "").strip()
            tech = proj.get("tech", "").strip()

            story.append(Paragraph(f"<b>{pname}</b>", role_style))
            if desc:
                story.append(Paragraph(f"•  {desc}", bullet_style))
            if tech:
                story.append(Paragraph(f"<b>Technologies:</b> {tech}", body_style))
            story.append(Spacer(1, 4))

    # ── EDUCATION ──
    if data.get("education"):
        section_header("Education")
        for edu in data["education"]:
            degree = edu.get("degree", "").strip()
            institution = edu.get("institution", "").strip()
            year = edu.get("year", "").strip()
            details = edu.get("details", "").strip()

            story.append(Paragraph(f"<b>{degree}</b>, {institution}", role_style))
            detail_line = " | ".join(filter(None, [year, details]))
            if detail_line:
                story.append(Paragraph(detail_line, date_style))
            story.append(Spacer(1, 4))

    # ── CERTIFICATIONS ──
    if data.get("certifications"):
        certs = [c.strip() for c in data["certifications"] if c.strip()]
        if certs:
            section_header("Certifications")
            for cert in certs:
                story.append(Paragraph(f"•  {cert}", bullet_style))

    doc.build(story)
    tailored_pdf = buffer.getvalue()

    # Save tailored resume to GridFS
    company = job.get("company_name", "job").replace(" ", "_")
    role = job.get("role", "role").replace(" ", "_")
    filename = f"tailored_{company}_{role}.pdf"
    file_id = save_resume_to_gridfs(tailored_pdf, filename, current_user)

    # Save metadata — overwrite existing tailored resume
    resumes_collection.delete_one({"user_id": current_user, "type": "tailored"})
    resumes_collection.insert_one({
        "user_id": current_user,
        "name": f"Tailored — {job.get('company_name','')} {job.get('role','')}",
        "filename": filename,
        "gridfs_id": file_id,
        "active": False,
        "type": "tailored",
        "job_id": job_id,
        "style": style,
        "uploaded_at": datetime.utcnow(),
        "text_preview": ""
    })

    return Response(
        content=tailored_pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
