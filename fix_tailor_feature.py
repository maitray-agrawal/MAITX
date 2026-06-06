# Add tailor endpoint to resume_routes.py
with open("app/resume_routes.py", encoding="utf-8") as f:
    content = f.read()

tailor_endpoint = '''
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

    jd = f"{job.get('company_name','')} - {job.get('role','')}\\n{job.get('eligibility','')}\\n{job.get('extra_notes','')}"

    style_instruction = """Format as a clean ATS-optimized resume. Use simple section headers, no tables or columns. 
    Prioritize keywords from the job description. Use action verbs and quantify achievements.""" if style == "ats" else """Format as a professional visually appealing resume. 
    Keep the candidate's original structure but enhance content for the target role."""

    prompt = f"""You are an expert resume writer. Rewrite this resume tailored specifically for the job below.

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
  "skills": ["skill1", "skill2", "skill3"],
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

    # Generate PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4,
        rightMargin=1.8*cm, leftMargin=1.8*cm,
        topMargin=1.5*cm, bottomMargin=1.5*cm)

    styles = getSampleStyleSheet()
    story = []

    # Color scheme
    accent_color = colors.HexColor("#7c6af7") if style == "ats" else colors.HexColor("#1a1a2e")
    
    name_style = ParagraphStyle("name", fontSize=22, fontName="Helvetica-Bold",
        textColor=accent_color, alignment=TA_CENTER, spaceAfter=4)
    contact_style = ParagraphStyle("contact", fontSize=9, fontName="Helvetica",
        textColor=colors.HexColor("#555555"), alignment=TA_CENTER, spaceAfter=12)
    section_style = ParagraphStyle("section", fontSize=11, fontName="Helvetica-Bold",
        textColor=accent_color, spaceBefore=14, spaceAfter=4)
    body_style = ParagraphStyle("body", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#222222"), spaceAfter=3, leading=14)
    bullet_style = ParagraphStyle("bullet", fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#333333"), spaceAfter=2, leading=13,
        leftIndent=12, bulletIndent=0)
    sub_style = ParagraphStyle("sub", fontSize=9, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#666666"), spaceAfter=2)

    def section_header(title):
        story.append(Paragraph(title.upper(), section_style))
        story.append(HRFlowable(width="100%", thickness=0.5, color=accent_color, spaceAfter=6))

    # Name & Contact
    story.append(Paragraph(data.get("name", ""), name_style))
    contact_parts = [p for p in [data.get("email"), data.get("phone"), data.get("linkedin")] if p]
    story.append(Paragraph(" · ".join(contact_parts), contact_style))

    # Summary
    if data.get("summary"):
        section_header("Professional Summary")
        story.append(Paragraph(data["summary"], body_style))

    # Skills
    if data.get("skills"):
        section_header("Skills")
        skills_text = " · ".join(data["skills"])
        story.append(Paragraph(skills_text, body_style))

    # Experience
    if data.get("experience"):
        section_header("Experience")
        for exp in data["experience"]:
            story.append(Paragraph(f"<b>{exp.get('title','')}</b> — {exp.get('company','')}", body_style))
            story.append(Paragraph(exp.get("duration", ""), sub_style))
            for bullet in exp.get("bullets", []):
                story.append(Paragraph(f"• {bullet}", bullet_style))
            story.append(Spacer(1, 6))

    # Projects
    if data.get("projects"):
        section_header("Projects")
        for proj in data["projects"]:
            story.append(Paragraph(f"<b>{proj.get('name','')}</b>", body_style))
            story.append(Paragraph(proj.get("description", ""), bullet_style))
            if proj.get("tech"):
                story.append(Paragraph(f"Tech: {proj['tech']}", sub_style))
            story.append(Spacer(1, 4))

    # Education
    if data.get("education"):
        section_header("Education")
        for edu in data["education"]:
            story.append(Paragraph(f"<b>{edu.get('degree','')}</b> — {edu.get('institution','')}", body_style))
            story.append(Paragraph(f"{edu.get('year','')}  {edu.get('details','')}", sub_style))

    # Certifications
    if data.get("certifications"):
        section_header("Certifications")
        for cert in data["certifications"]:
            story.append(Paragraph(f"• {cert}", bullet_style))

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
'''

# Append to resume_routes.py
content += tailor_endpoint
with open("app/resume_routes.py", "w", encoding="utf-8") as f:
    f.write(content)
print("resume_routes.py updated with tailor endpoint")