content = open('maitx-dashboard/src/App.js', encoding='utf-8').read()

old = "{job.eligibility && <p style={{ fontSize: \"0.75rem\", color: G.t3, marginBottom: 4 }}>🎓 {job.eligibility}</p>}"

new = """{job.ats_score !== null && job.ats_score !== undefined && (
        <span style={{ display: 'inline-block', fontSize: '0.7rem', fontWeight: 700, color: job.ats_score >= 70 ? G.green : job.ats_score >= 50 ? G.amber : G.red, background: job.ats_score >= 70 ? G.greenSoft : job.ats_score >= 50 ? G.amberSoft : G.redSoft, border: '1px solid ' + (job.ats_score >= 70 ? G.greenBorder : job.ats_score >= 50 ? G.amberBorder : G.red + '40'), borderRadius: 20, padding: '2px 9px', marginBottom: 8 }}>ATS {job.ats_score}%</span>
      )}
      {job.eligibility && <p style={{ fontSize: \"0.75rem\", color: G.t3, marginBottom: 4 }}>🎓 {job.eligibility}</p>}"""

if old in content:
    content = content.replace(old, new)
    open('maitx-dashboard/src/App.js', 'w', encoding='utf-8').write(content)
    print('ATS badge added to job cards')
else:
    print('Pattern not found - check manually')
