with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Add TailorSection component before ResumeResults
tailor_section = '''
function TailorSection({ token, jobId, onDone }) {
  const [style, setStyle] = useState("ats");
  const [loading, setLoading] = useState(false);
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const tailor = async () => {
    if (!jobId) { setError("No job selected. Go back and click Tailor from a job card."); return; }
    setLoading(true); setError("");
    try {
      const form = new FormData();
      form.append("style", style);
      const res = await fetch(`${API_BASE}/api/resume/tailor/${jobId}`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: form
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Tailoring failed");
      }
      const blob = await res.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url; a.download = "tailored_resume.pdf"; a.click();
      URL.revokeObjectURL(url);
      setDone(true);
      if (onDone) onDone();
    } catch(e) {
      setError(e.message || "Tailoring failed");
    } finally { setLoading(false); }
  };

  const G2 = { accent: "#7c6af7", accentSoft: "#7c6af712", accentBorder: "#7c6af740", border: "#25253a", b1: "#0f0f1a", b2: "#14141f", t1: "#eeeef8", t2: "#8888aa", t3: "#44445a", green: "#34d399", greenSoft: "#34d39912", greenBorder: "#34d39930", amber: "#fbbf24", amberSoft: "#fbbf2412" };

  return (
    <div style={{ background: G2.b2, borderRadius: 16, padding: 24, border: `1px solid ${G2.border}`, marginTop: 16 }}>
      <p style={{ fontSize: "0.68rem", letterSpacing: "0.12em", color: G2.t3, textTransform: "uppercase", marginBottom: 16 }}>Tailor My Resume</p>
      <p style={{ fontSize: "0.85rem", color: G2.t2, marginBottom: 16 }}>Choose your preferred resume style. AI will rewrite your resume optimized for this specific job.</p>
      <div style={{ display: "flex", gap: 10, marginBottom: 20 }}>
        {[["ats", "🤖 ATS Friendly", "Simple format, keyword-optimized, passes automated screening"], ["original", "✨ Professional", "Polished layout, enhanced content, visually impressive"]].map(([val, label, desc]) => (
          <div key={val} onClick={() => setStyle(val)}
            style={{ flex: 1, padding: 16, borderRadius: 12, border: `2px solid ${style === val ? G2.accent : G2.border}`, background: style === val ? G2.accentSoft : G2.b1, cursor: "pointer" }}>
            <p style={{ fontSize: "0.88rem", fontWeight: 600, color: style === val ? G2.accent : G2.t1, marginBottom: 4 }}>{label}</p>
            <p style={{ fontSize: "0.75rem", color: G2.t3 }}>{desc}</p>
          </div>
        ))}
      </div>
      {error && <p style={{ color: "#f87171", fontSize: "0.8rem", marginBottom: 12 }}>{error}</p>}
      {done
        ? <p style={{ color: G2.green, fontSize: "0.88rem" }}>✓ Tailored resume downloaded and saved!</p>
        : <button onClick={tailor} disabled={loading}
            style={{ width: "100%", background: G2.accent, color: "#fff", border: "none", borderRadius: 10, padding: "12px", fontSize: "0.92rem", fontWeight: 600, cursor: loading ? "not-allowed" : "pointer", opacity: loading ? 0.7 : 1, fontFamily: "inherit" }}>
            {loading ? "✨ Tailoring your resume..." : "Generate & Download Tailored Resume"}
          </button>
      }
    </div>
  );
}

'''

# Insert TailorSection before ResumeResults
content = content.replace(
    'function ResumeResults(',
    tailor_section + 'function ResumeResults('
)

# Add jobId and token props to ResumeResults
content = content.replace(
    'function ResumeResults({ result, onBack })',
    'function ResumeResults({ result, onBack, token, jobId })'
)

# Add TailorSection at the bottom of ResumeResults before closing
content = content.replace(
    "if (result) return <ResumeResults result={result} onBack={() => setResult(null)} />;",
    "if (result) return <ResumeResults result={result} onBack={() => setResult(null)} token={token} jobId={prefilledJob?._id} />;"
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("TailorSection added to App.js")