with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Add back button at the top of ResumeTailor return
content = content.replace(
    'function ResumeTailor({ token, prefilledJob, onBack }) {',
    'function ResumeTailor({ token, prefilledJob, onBack }) {'
)

# Find the ResumeTailor return and add back button at top
content = content.replace(
    '  return (\n    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0 auto" }}>\n      {/* Header */}',
    '''  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0 auto" }}>
      {onBack && (
        <button onClick={onBack} style={{ background: "transparent", color: G.t2, border: `1px solid ${G.border}`, borderRadius: 9, padding: "7px 14px", fontSize: "0.82rem", fontFamily: "inherit", cursor: "pointer", marginBottom: 20, display: "flex", alignItems: "center", gap: 6 }}>← Back to Dashboard</button>
      )}
      {/* Header */}'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Back button added")