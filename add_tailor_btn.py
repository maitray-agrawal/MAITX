content = open('maitx-dashboard/src/App.js', encoding='utf-8').read()

old = '{!job.applied && (\n          <button className="btn" onClick={() => onMarkApplied(job._id)}'
new = '{onTailor && (\n          <button className="btn" onClick={() => onTailor(job)} style={{ background: "#7c6af712", color: "#7c6af7", padding: "6px 12px", borderRadius: 8, border: "1px solid #7c6af740", fontSize: "0.78rem", fontFamily: "inherit" }}>\u2728 Tailor</button>\n        )}\n        {!job.applied && (\n          <button className="btn" onClick={() => onMarkApplied(job._id)}'

result = content.replace(old, new)
open('maitx-dashboard/src/App.js', 'w', encoding='utf-8').write(result)
print('done:', result.count('onTailor(job)'), 'occurrences')