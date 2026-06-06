content = open('app/resume_routes.py', encoding='utf-8').read()
content = content.replace(
    'if not resume_text or len(resume_text) < 50:\n        raise HTTPException(status_code=400, detail="Could not extract text from PDF")',
    'if not resume_text or len(resume_text) < 50:\n        raise HTTPException(status_code=400, detail="Could not extract text from resume PDF")'
)
content = content.replace(
    'if len(jd.strip()) < 3:\n        raise HTTPException(status_code=400, detail="Enter at least a role or keywords")',
    'if len(jd.strip()) < 2:\n        raise HTTPException(status_code=400, detail="Enter at least a role or keywords")'
)
open('app/resume_routes.py', 'w', encoding='utf-8').write(content)
print('done')
