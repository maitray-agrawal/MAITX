content = open('app/resume_routes.py', encoding='utf-8').read()
content = content.replace(
    'if len(jd.strip()) < 50:\n        raise HTTPException(status_code=400, detail="Job description too short")',
    'if len(jd.strip()) < 3:\n        raise HTTPException(status_code=400, detail="Enter at least a role or keywords")'
)
open('app/resume_routes.py', 'w', encoding='utf-8').write(content)
print('Backend validation fixed')
