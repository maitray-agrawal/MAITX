with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Add apply link button and deadline urgency to JobCard
# After extra_notes line, before the action buttons
old = '{job.extra_notes && <p style={{ fontSize: "0.73rem", color: G.t3, fontStyle: "italic", marginBottom: 8 }}>🔍'
new = '''{job.extra_notes && <p style={{ fontSize: "0.73rem", color: G.t3, fontStyle: "italic", marginBottom: 8 }}>🔍'''

# Fix 2: Add Apply Now button that opens link
content = content.replace(
    '<button className="btn" onClick={() => onDelete(job._id)} style={{ background: "transparent", color:G.t3, padding: "6px 10px", borderRadius: 8, border: `1px solid ${G.border}`, fontSize: "0.78rem", marginLeft: "auto" }}>✕</button>',
    '''{job.apply_link && (
        <a href={job.apply_link} target="_blank" rel="noopener noreferrer" style={{ textDecoration: "none" }}>
          <button className="btn" style={{ background: G.accentSoft, color: G.accent, padding: "6px 12px", borderRadius: 8, border: `1px solid ${G.accentBorder}`, fontSize: "0.78rem", fontFamily: "'DM Sans',sans-serif" }}>Apply →</button>
        </a>
      )}
      <button className="btn" onClick={() => onDelete(job._id)} style={{ background: "transparent", color:G.t3, padding: "6px 10px", borderRadius: 8, border: `1px solid ${G.border}`, fontSize: "0.78rem", marginLeft: "auto" }}>✕</button>'''
)

# Fix 3: Add deadline urgency color to deadline tag
content = content.replace(
    '{[["📅", job.deadline], ["💰", job.stipend], ["🏢", job.work_format], ["📍", job.location]].filter(([, v]) => v).map(([icon, val]) => (\n          <span key={val} style={{ fontSize: "0.73rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 6, padding: "2px 8px" }}>{icon} {val}</span>',
    '''{[["📅", job.deadline], ["💰", job.stipend], ["🏢", job.work_format], ["📍", job.location]].filter(([, v]) => v).map(([icon, val]) => {
          const isDeadline = icon === "📅";
          const isUrgent = isDeadline && val && (() => { try { const d = new Date(val); const days = Math.ceil((d - new Date()) / 86400000); return days >= 0 && days <= 3; } catch { return false; } })();
          const isSoon = isDeadline && val && (() => { try { const d = new Date(val); const days = Math.ceil((d - new Date()) / 86400000); return days > 3 && days <= 7; } catch { return false; } })();
          return (<span key={val} style={{ fontSize: "0.73rem", color: isUrgent ? G.red : isSoon ? G.amber : G.t2, background: isUrgent ? G.redSoft : isSoon ? G.amberSoft : G.b1, border: `1px solid ${isUrgent ? G.red : isSoon ? G.amber : G.border}`, borderRadius: 6, padding: "2px 8px", fontWeight: isUrgent ? 600 : 400 }}>{icon} {val}{isUrgent ? " ⚠️" : isSoon ? " ⏰" : ""}</span>'''
)

content = content.replace(
    '          <span key={val} style={{ fontSize: "0.73rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 6, padding: "2px 8px" }}>{icon} {val}</span>\n        ))}\n      </div>',
    '''        );\n        })}
      </div>'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Dashboard UX fixes applied")