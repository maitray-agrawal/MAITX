content = open("maitx-dashboard/src/App.js", encoding="utf-8").read()

# Replace the ResumeTailor component entirely
old = content[content.index("function ResumeTailor"):content.index("function BentoStat")]

new = '''function ResumeTailor({ token }) {
  const [resumes, setResumes] = useState([]);
  const [activeTab, setActiveTab] = useState("manage");
  const [uploading, setUploading] = useState(false);
  const [resumeName, setResumeName] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [setAsActive, setSetAsActive] = useState(true);
  const [jd, setJd] = useState("");
  const [selectedResumeId, setSelectedResumeId] = useState("");
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const fileRef = useRef();

  const h = { headers: { Authorization: `Bearer ${token}` } };

  const fetchResumes = async () => {
    try {
      const r = await axios.get(`${API_BASE}/api/resume/list`, h);
      setResumes(r.data);
      const active = r.data.find(r => r.active);
      if (active) setSelectedResumeId(active.id);
    } catch (e) { console.error(e); }
  };

  useEffect(() => { fetchResumes(); }, []);

  const uploadResume = async () => {
    if (!uploadFile) { setError("Select a PDF file"); return; }
    if (!resumeName.trim()) { setError("Enter a name for this resume"); return; }
    setUploading(true); setError("");
    try {
      const form = new FormData();
      form.append("resume", uploadFile);
      form.append("name", resumeName);
      form.append("set_active", setAsActive);
      await axios.post(`${API_BASE}/api/resume/upload`, form, {
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
      });
      setUploadFile(null); setResumeName(""); setSetAsActive(true);
      await fetchResumes();
    } catch (e) {
      setError(e.response?.data?.detail || "Upload failed");
    } finally { setUploading(false); }
  };

  const setActive = async (id) => {
    await axios.post(`${API_BASE}/api/resume/set-active/${id}`, {}, h);
    await fetchResumes();
  };

  const deleteResume = async (id) => {
    await axios.delete(`${API_BASE}/api/resume/${id}`, h);
    await fetchResumes();
  };

  const analyze = async () => {
    if (jd.trim().length < 3) { setError("Enter at least a role or keywords"); return; }
    setAnalyzing(true); setError("");
    try {
      const form = new FormData();
      form.append("jd", jd);
      if (selectedResumeId) form.append("resume_id", selectedResumeId);
      const r = await axios.post(`${API_BASE}/api/resume/analyze`, form, {
        headers: { Authorization: `Bearer ${token}`, "Content-Type": "multipart/form-data" }
      });
      setResult(r.data);
    } catch (e) {
      setError(e.response?.data?.detail || "Analysis failed");
    } finally { setAnalyzing(false); }
  };

  if (result) return <ResumeResults result={result} onBack={() => setResult(null)} />;

  const cardStyle = { background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}`, marginBottom: 12 };
  const inputStyle = { width: "100%", background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10, padding: "10px 14px", color: G.t1, fontSize: "0.88rem", fontFamily: "inherit", boxSizing: "border-box" };

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0 auto" }}>
      <div style={{ marginBottom: 24 }}>
        <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>AI-Powered</p>
        <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>Resume Tailor</h1>
      </div>

      {/* Sub tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {[["manage", "📁 My Resumes"], ["analyze", "✨ Analyze"]].map(([id, label]) => (
          <button key={id} onClick={() => setActiveTab(id)}
            style={{ padding: "8px 18px", borderRadius: 10, border: `1px solid ${activeTab === id ? G.accent : G.border}`, background: activeTab === id ? G.accentSoft : "transparent", color: activeTab === id ? G.accent : G.t2, cursor: "pointer", fontSize: "0.84rem", fontFamily: "inherit", fontWeight: activeTab === id ? 600 : 400 }}>
            {label}
          </button>
        ))}
      </div>

      {/* Manage tab */}
      {activeTab === "manage" && (
        <>
          {/* Upload */}
          <div style={cardStyle}>
            <p style={{ fontSize: "0.72rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 14 }}>Upload New Resume</p>
            <input placeholder="Resume name (e.g. General, Data Science)" value={resumeName}
              onChange={e => setResumeName(e.target.value)}
              style={{ ...inputStyle, marginBottom: 10 }} />
            <div onClick={() => fileRef.current.click()}
              style={{ border: `2px dashed ${uploadFile ? G.accent : G.border}`, borderRadius: 12, padding: "20px", textAlign: "center", cursor: "pointer", background: uploadFile ? G.accentSoft : "transparent", marginBottom: 10 }}>
              <p style={{ fontSize: "0.88rem", color: uploadFile ? G.accent : G.t2 }}>
                {uploadFile ? uploadFile.name : "Click to select PDF"}
              </p>
            </div>
            <input ref={fileRef} type="file" accept=".pdf" style={{ display: "none" }}
              onChange={e => setUploadFile(e.target.files[0] || null)} />
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
              <input type="checkbox" id="setActive" checked={setAsActive} onChange={e => setSetAsActive(e.target.checked)} />
              <label htmlFor="setActive" style={{ fontSize: "0.82rem", color: G.t2, cursor: "pointer" }}>Set as active resume for auto-analysis</label>
            </div>
            <button onClick={uploadResume} disabled={uploading} className="btn"
              style={{ background: G.accent, color: "#fff", padding: "10px 20px", borderRadius: 10, fontSize: "0.88rem", fontWeight: 600, fontFamily: "inherit", opacity: uploading ? 0.7 : 1 }}>
              {uploading ? "Uploading..." : "Upload Resume"}
            </button>
            {error && <p style={{ color: G.red, fontSize: "0.8rem", marginTop: 10 }}>{error}</p>}
          </div>

          {/* Saved resumes */}
          <div style={cardStyle}>
            <p style={{ fontSize: "0.72rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 14 }}>{resumes.length} Saved Resume{resumes.length !== 1 ? "s" : ""}</p>
            {resumes.length === 0
              ? <p style={{ color: G.t3, fontSize: "0.85rem" }}>No resumes uploaded yet</p>
              : resumes.map((r, i) => (
                <div key={r.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: i < resumes.length - 1 ? `1px solid ${G.border}` : "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: "1.2rem" }}>📄</span>
                    <div>
                      <p style={{ fontSize: "0.88rem", fontWeight: 600, color: G.t1 }}>{r.name}</p>
                      <p style={{ fontSize: "0.72rem", color: G.t3 }}>{r.filename} · {new Date(r.uploaded_at).toLocaleDateString()}</p>
                    </div>
                    {r.active && <span style={{ fontSize: "0.68rem", color: G.green, background: G.greenSoft, border: `1px solid ${G.greenBorder}`, borderRadius: 20, padding: "2px 8px" }}>Active</span>}
                  </div>
                  <div style={{ display: "flex", gap: 8 }}>
                    {!r.active && (
                      <button onClick={() => setActive(r.id)} className="btn"
                        style={{ background: G.accentSoft, color: G.accent, border: `1px solid ${G.accentBorder}`, borderRadius: 8, padding: "5px 10px", fontSize: "0.75rem" }}>
                        Set Active
                      </button>
                    )}
                    <button onClick={() => deleteResume(r.id)} className="btn"
                      style={{ background: G.redSoft, color: G.red, border: `1px solid ${G.red}40`, borderRadius: 8, padding: "5px 10px", fontSize: "0.75rem" }}>
                      Delete
                    </button>
                  </div>
                </div>
              ))
            }
          </div>
        </>
      )}

      {/* Analyze tab */}
      {activeTab === "analyze" && (
        <>
          <div style={cardStyle}>
            <p style={{ fontSize: "0.72rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 14 }}>Select Resume</p>
            {resumes.length === 0
              ? <p style={{ color: G.red, fontSize: "0.85rem" }}>No resumes saved. Go to My Resumes tab to upload one.</p>
              : <div style={{ display: "flex", flexWrap: "wrap", gap: 8 }}>
                  {resumes.map(r => (
                    <button key={r.id} onClick={() => setSelectedResumeId(r.id)}
                      style={{ padding: "8px 16px", borderRadius: 10, border: `1px solid ${selectedResumeId === r.id ? G.accent : G.border}`, background: selectedResumeId === r.id ? G.accentSoft : "transparent", color: selectedResumeId === r.id ? G.accent : G.t2, cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit" }}>
                      {r.name} {r.active ? "⭐" : ""}
                    </button>
                  ))}
                </div>
            }
          </div>

          <div style={cardStyle}>
            <p style={{ fontSize: "0.72rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>Job Description or Keywords</p>
            <textarea value={jd} onChange={e => setJd(e.target.value)}
              placeholder="Paste JD or type keywords: data science, Python, ML, LLM..." rows={6}
              style={{ ...inputStyle, resize: "vertical", marginBottom: 0 }} />
          </div>

          {error && <div style={{ background: G.redSoft, border: `1px solid ${G.red}40`, borderRadius: 10, padding: "10px 14px", marginBottom: 14, fontSize: "0.82rem", color: G.red }}>{error}</div>}

          <button onClick={analyze} disabled={analyzing || resumes.length === 0} className="btn"
            style={{ width: "100%", background: analyzing ? G.b3 : G.accent, color: "#fff", padding: "14px", borderRadius: 12, fontSize: "1rem", fontWeight: 700, fontFamily: "inherit" }}>
            {analyzing ? (
              <span style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 10 }}>
                <span style={{ width: 16, height: 16, border: "2px solid #fff4", borderTop: "2px solid #fff", borderRadius: "50%", display: "inline-block", animation: "spin 0.8s linear infinite" }} />
                Analyzing with AI...
              </span>
            ) : "Analyze Resume →"}
          </button>
        </>
      )}
    </div>
  );
}

'''

content = content[:content.index("function ResumeTailor")] + new + content[content.index("function BentoStat"):]

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("ResumeTailor component updated")