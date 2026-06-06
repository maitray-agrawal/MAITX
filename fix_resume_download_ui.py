with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Add download button next to delete button in resume list
content = content.replace(
    '<button onClick={() => deleteResume(r.id)}',
    '''<a href={`${API_BASE}/api/resume/download/${r.id}`}
              onClick={async (e) => {
                e.preventDefault();
                const res = await fetch(`${API_BASE}/api/resume/download/${r.id}`, { headers: { Authorization: `Bearer ${token}` } });
                const blob = await res.blob();
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a"); a.href = url; a.download = r.filename || "resume.pdf"; a.click();
                URL.revokeObjectURL(url);
              }}
              style={{ textDecoration: "none" }}>
              <button style={{ background: "transparent", color: G.accent, border: `1px solid ${G.accentBorder}`, borderRadius: 7, padding: "4px 10px", fontSize: "0.75rem", cursor: "pointer", fontFamily: "inherit" }}>↓ PDF</button>
            </a>
            <button onClick={() => deleteResume(r.id)}'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("App.js updated with resume download button")