with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Fix 1: Add back button inside ResumeTailor header
content = content.replace(
    '''  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0auto" }}>
      <div style={{ marginBottom: 24 }}>
        <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>AI-Powered</p>
        <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>Resume Tailor</h1>
      </div>''',
    '''  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0auto" }}>
      {onBack && (
        <button onClick={onBack} style={{ background: "transparent", color: G.t2, border: `1px solid ${G.border}`, borderRadius: 9, padding: "7px 14px", fontSize: "0.82rem", fontFamily: "inherit", cursor: "pointer", marginBottom: 20, display: "inline-flex", alignItems: "center", gap: 6 }}>← Back to Dashboard</button>
      )}
      <div style={{ marginBottom: 24 }}>
        <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>AI-Powered</p>
        <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>Resume Tailor</h1>
      </div>'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Back button added to ResumeTailor")