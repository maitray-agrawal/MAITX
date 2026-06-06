# Add download endpoint to resume_routes.py
with open("app/resume_routes.py", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    '# Auto-analyze a specific job against active resume',
    '''# Download resume PDF
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

# Auto-analyze a specific job against active resume'''
)

with open("app/resume_routes.py", "w", encoding="utf-8") as f:
    f.write(content)
print("resume_routes.py updated with download endpoint")