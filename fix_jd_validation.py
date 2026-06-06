import re

content = open('maitx-dashboard/src/App.js', encoding='utf-8').read()

# Fix frontend validation - lower limit to 3 chars
content = content.replace(
    'if (jd.trim().length < 50) { setError("Paste a job description (min 50 chars)"); return; }',
    'if (jd.trim().length < 3) { setError("Enter at least a role or keywords"); return; }'
)

open('maitx-dashboard/src/App.js', 'w', encoding='utf-8').write(content)
print('Frontend validation fixed')
