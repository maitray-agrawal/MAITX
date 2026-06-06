
import { useState, useEffect, useCallback, useRef } from "react";
import axios from "axios";
import AdminPanel from "./AdminPanel";

const API_BASE = "https://web-production-c1e12.up.railway.app";

const G = {
  bg: "#080810", b1: "#0f0f1a", b2: "#14141f", b3: "#1a1a28",
  border: "#25253a", borderHi: "#35355a",
  accent: "#7c6af7", accentSoft: "#7c6af712", accentBorder: "#7c6af740",
  green: "#34d399", greenSoft: "#34d39912", greenBorder: "#34d39930",
  amber: "#fbbf24", amberSoft: "#fbbf2412",
  red: "#f87171", redSoft: "#f8717112",
  t1: "#eeeef8", t2: "#8888aa", t3: "#44445a",
};

const injectStyles = () => {
  if (document.getElementById("maitx-styles")) return;
  const s = document.createElement("style");
  s.id = "maitx-styles";
  s.textContent = `
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:ital,wght@0,300;0,400;0,500;1,400&display=swap');
    *{box-sizing:border-box;margin:0;padding:0}
    body{background:${G.bg};color:${G.t1};font-family:'DM Sans',sans-serif;-webkit-font-smoothing:antialiased}
    ::-webkit-scrollbar{width:3px}::-webkit-scrollbar-thumb{background:${G.border};border-radius:2px}
    @keyframes fadeUp{from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
    @keyframes shimmer{from{background-position:-400% 0}to{background-position:400% 0}}
    @keyframes spin{to{transform:rotate(360deg)}}
    .bento-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:10px}
    .bento-grid-2{display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:10px}
    @media(max-width:600px){.bento-grid{grid-template-columns:1fr!important}.bento-grid-2{grid-template-columns:1fr!important}}
    .job-card{background:${G.b2};border-radius:16px;padding:18px 20px;margin-bottom:8px;border:1px solid ${G.border};transition:all 0.18s ease;animation:fadeUp 0.3s ease both}
    .job-card:hover{background:${G.b3};border-color:${G.borderHi};transform:translateY(-1px)}
    .btn{cursor:pointer;border:none;font-family:'DM Sans',sans-serif;transition:all 0.15s ease}
    .btn:active{transform:scale(0.97)}
    input:focus{outline:none;border-color:${G.accent}!important}
    .filter-btn{padding:7px 16px;border-radius:9px;border:1px solid ${G.border};background:transparent;color:${G.t2};cursor:pointer;font-size:0.8rem;font-family:'DM Sans',sans-serif;transition:all 0.15s}
    .filter-btn.active{border-color:${G.accent};background:${G.accentSoft};color:${G.accent};font-weight:500}
    .shimmer{background:linear-gradient(90deg,${G.b3} 25%,${G.border} 50%,${G.b3} 75%);background-size:400% 100%;animation:shimmer 1.8s infinite}
    @keyframes otpPulse{0%,100%{border-color:${G.accentBorder}}50%{border-color:${G.accent}}}
    .otp-sent{animation:otpPulse 2s ease infinite}
    @keyframes pulse{0%,100%{opacity:1}50%{opacity:0.5}}
  `;
  document.head.appendChild(s);
};

const getToken = () => localStorage.getItem("maitx_token");
const getStoredUser = () => localStorage.getItem("maitx_user");
const authHeaders = () => ({ headers: { Authorization: `Bearer ${getToken()}` } });

function ScoreRing({ score }) {
  const color = score >= 70 ? G.green : score >= 50 ? G.amber : G.red;
  const r = 36; const circ = 2 * Math.PI * r;
  const dash = (score / 100) * circ;
  return (
    <div style={{ position: "relative", width: 100, height: 100, flexShrink: 0 }}>
      <svg width="100" height="100" style={{ transform: "rotate(-90deg)" }}>
        <circle cx="50" cy="50" r={r} fill="none" stroke={G.border} strokeWidth="8" />
        <circle cx="50" cy="50" r={r} fill="none" stroke={color} strokeWidth="8"
          strokeDasharray={`${dash} ${circ}`} strokeLinecap="round"
          style={{ transition: "stroke-dasharray 1s ease" }} />
      </svg>
      <div style={{ position: "absolute", inset: 0, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center" }}>
        <span style={{ fontSize: "1.4rem", fontWeight: 800, color, fontFamily: "'Syne',sans-serif" }}>{score}</span>
        <span style={{ fontSize: "0.6rem", color: G.t3 }}>/ 100</span>
      </div>
    </div>
  );
}


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

function ResumeResults({ result, onBack, token, jobId }) {
  const [tab, setTab] = useState("overview");
  const tabs = ["overview", "keywords", "improvements", "bullets", "ats"];

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
        <button onClick={onBack} className="btn"
          style={{ background: G.b2, color: G.t2, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem" }}>← Back</button>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase" }}>Resume Analysis</p>
          <h1 style={{ fontSize: "1.6rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>Tailor Report</h1>
        </div>
      </div>

      {/* Score header */}
      <div style={{ background: G.b2, borderRadius: 20, padding: 24, border: `1px solid ${G.border}`, marginBottom: 16, display: "flex", gap: 24, alignItems: "center", flexWrap: "wrap" }}>
        <ScoreRing score={result.match_score} />
        <div style={{ flex: 1, minWidth: 200 }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>Overall Match</p>
          <p style={{ fontSize: "0.88rem", color: G.t2, lineHeight: 1.5, marginBottom: 16 }}>{result.summary}</p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 8 }}>
            {Object.entries(result.score_breakdown || {}).map(([k, v]) => (
              <div key={k} style={{ background: G.b1, borderRadius: 10, padding: "10px 12px", border: `1px solid ${G.border}` }}>
                <p style={{ fontSize: "0.65rem", color: G.t3, textTransform: "uppercase", marginBottom: 4 }}>{k.replace("_", " ")}</p>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <div style={{ flex: 1, height: 4, borderRadius: 2, background: G.border }}>
                    <div style={{ width: `${v}%`, height: "100%", borderRadius: 2, background: v >= 70 ? G.green : v >= 50 ? G.amber : G.red }} />
                  </div>
                  <span style={{ fontSize: "0.75rem", fontWeight: 700, color: G.t1 }}>{v}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        {tabs.map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "7px 16px", borderRadius: 9, border: `1px solid ${tab === t ? G.accent : G.border}`, background: tab === t ? G.accentSoft : "transparent", color: tab === t ? G.accent : G.t2, cursor: "pointer", fontSize: "0.8rem", fontFamily: "inherit", fontWeight: tab === t ? 600 : 400 }}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === "overview" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            <p style={{ fontSize: "0.68rem", color: G.green, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>✓ Strong Sections</p>
            {(result.strong_sections || []).map((s, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8 }}>
                <span style={{ width: 6, height: 6, borderRadius: "50%", background: G.green, flexShrink: 0 }} />
                <span style={{ fontSize: "0.85rem", color: G.t1 }}>{s}</span>
              </div>
            ))}
          </div>
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            <p style={{ fontSize: "0.68rem", color: G.red, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>✗ Needs Work</p>
            {(result.weak_sections || []).map((s, i) => (
              <div key={i} style={{ marginBottom: 10 }}>
                <p style={{ fontSize: "0.85rem", color: G.t1, fontWeight: 500 }}>{s.section}</p>
                <p style={{ fontSize: "0.75rem", color: G.red, marginTop: 2 }}>{s.issue}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Keywords */}
      {tab === "keywords" && (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            <p style={{ fontSize: "0.68rem", color: G.green, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>✓ Matched Keywords</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {(result.matched_keywords || []).map((k, i) => (
                <span key={i} style={{ fontSize: "0.78rem", color: G.green, background: G.greenSoft, border: `1px solid ${G.greenBorder}`, borderRadius: 20, padding: "3px 10px" }}>{k}</span>
              ))}
            </div>
          </div>
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            <p style={{ fontSize: "0.68rem", color: G.red, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 12 }}>✗ Missing Keywords</p>
            <div style={{ display: "flex", flexWrap: "wrap", gap: 6 }}>
              {(result.missing_keywords || []).map((k, i) => (
                <span key={i} style={{ fontSize: "0.78rem", color: G.red, background: G.redSoft, border: `1px solid ${G.red}40`, borderRadius: 20, padding: "3px 10px" }}>{k}</span>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Improvements */}
      {tab === "improvements" && (
        <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>Section Fixes</p>
          {(result.weak_sections || []).map((s, i) => (
            <div key={i} style={{ marginBottom: 16, padding: 16, background: G.b1, borderRadius: 12, border: `1px solid ${G.border}` }}>
              <p style={{ fontSize: "0.88rem", fontWeight: 600, color: G.t1, marginBottom: 6 }}>{s.section}</p>
              <p style={{ fontSize: "0.78rem", color: G.red, marginBottom: 8 }}>Issue: {s.issue}</p>
              <p style={{ fontSize: "0.78rem", color: G.green }}>Fix: {s.fix}</p>
            </div>
          ))}
        </div>
      )}

      {/* Bullets */}
      {tab === "bullets" && (
        <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>Rewritten Bullet Points</p>
          {(result.rewritten_bullets || []).map((b, i) => (
            <div key={i} style={{ marginBottom: 16, padding: 16, background: G.b1, borderRadius: 12, border: `1px solid ${G.border}` }}>
              <p style={{ fontSize: "0.72rem", color: G.t3, marginBottom: 6 }}>ORIGINAL</p>
              <p style={{ fontSize: "0.82rem", color: G.t2, marginBottom: 10, fontStyle: "italic" }}>{b.original}</p>
              <p style={{ fontSize: "0.72rem", color: G.green, marginBottom: 6 }}>IMPROVED</p>
              <p style={{ fontSize: "0.85rem", color: G.t1 }}>{b.improved}</p>
            </div>
          ))}
        </div>
      )}

      {/* ATS Tips */}
      {tab === "ats" && (
        <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 16 }}>ATS Optimization Tips</p>
          {(result.ats_tips || []).map((tip, i) => (
            <div key={i} style={{ display: "flex", gap: 12, marginBottom: 14, padding: 14, background: G.b1, borderRadius: 12, border: `1px solid ${G.border}` }}>
              <span style={{ fontSize: "1rem", flexShrink: 0 }}>💡</span>
              <p style={{ fontSize: "0.85rem", color: G.t1, lineHeight: 1.5 }}>{tip}</p>
            </div>
          ))}
        </div>
      <TailorSection token={token} jobId={jobId} />
      )}
    </div>
  );
}

function ResumeTailor({ token, prefilledJob, onBack }) {
  const [resumes, setResumes] = useState([]);
  const [activeTab, setActiveTab] = useState("manage");
  const [uploading, setUploading] = useState(false);
  const [resumeName, setResumeName] = useState("");
  const [uploadFile, setUploadFile] = useState(null);
  const [setAsActive, setSetAsActive] = useState(true);
  const [jd, setJd] = useState("");
  const [autoAnalyzing, setAutoAnalyzing] = useState(false);
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

  useEffect(() => {
    if (prefilledJob) {
      const jdText = [
        prefilledJob.company_name,
        prefilledJob.role,
        prefilledJob.eligibility,
        prefilledJob.extra_notes,
        prefilledJob.work_format,
        prefilledJob.location
      ].filter(Boolean).join("\n");
      setJd(jdText);
      setActiveTab("analyze");
    }
  }, [prefilledJob]);

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

  if (result) return <ResumeResults result={result} onBack={() => setResult(null)} token={token} jobId={prefilledJob?._id} />;

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
                    <a href={`${API_BASE}/api/resume/download/${r.id}`}
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

function BentoStat({ label, value, color, soft, sub }) {
  return (
    <div style={{ background: G.b2, borderRadius: 16, padding: "20px", border: `1px solid ${G.border}`, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", bottom: -16, right: -16, width: 64, height: 64, borderRadius: "50%", background: soft }} />
      <p style={{ fontSize: "0.7rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 10 }}>{label}</p>
      <p style={{ fontSize: "2.4rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color, lineHeight: 1 }}>{value}</p>
      {sub && <p style={{ fontSize: "0.72rem", color: G.t3, marginTop: 6 }}>{sub}</p>}
    </div>
  );
}

function ApplyRateBox({ jobs }) {
  const total = jobs.length;
  const applied = jobs.filter(j => j.applied).length;
  const pct = total > 0 ? Math.round((applied / total) * 100) : 0;
  const bars = 8;
  return (
    <div style={{ background: G.b2, borderRadius: 16, padding: "20px", border: `1px solid ${G.border}`, gridColumn: "span 2" }}>
      <p style={{ fontSize: "0.7rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 14 }}>Apply rate</p>
      <div style={{ display: "flex", alignItems: "baseline", gap: 8, marginBottom: 14 }}>
        <span style={{ fontSize: "2.4rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.green }}>{pct}%</span>
        <span style={{ fontSize: "0.8rem", color: G.t3 }}>{applied} of {total} applied</span>
      </div>
      <div style={{ display: "flex", gap: 4 }}>
        {Array.from({ length: bars }).map((_, i) => (
          <div key={i} style={{ flex: 1, height: 6, borderRadius: 3, background: i < Math.round((pct / 100) * bars) ? G.green : G.border }} />
        ))}
      </div>
    </div>
  );
}

function RecentActivity({ jobs }) {
  const recent = [...jobs].slice(0, 3);
  return (
    <div style={{ background: G.b2, borderRadius: 16, padding: "20px", border: `1px solid ${G.border}`, gridColumn: "span 3" }}>
      <p style={{ fontSize: "0.7rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 14 }}>Recent saves</p>
      {recent.length === 0
        ? <p style={{ color: G.t3, fontSize: "0.82rem" }}>No jobs saved yet</p>
        : recent.map((j, i) => (
          <div key={j._id} style={{ display: "flex", alignItems: "center", justifyContent: "space-between", paddingBottom: i < recent.length - 1 ? 10 : 0, marginBottom: i < recent.length - 1 ? 10 : 0, borderBottom: i < recent.length - 1 ? `1px solid ${G.border}` : "none" }}>
            <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
              <div style={{ width: 8, height: 8, borderRadius: "50%", background: j.applied ? G.green : G.accent, flexShrink: 0 }} />
              <div>
                <p style={{ fontSize: "0.85rem", fontWeight: 500, color: G.t1 }}>{j.company_name}</p>
                <p style={{ fontSize: "0.75rem", color: G.t2 }}>{j.role}</p>
              </div>
            </div>
            <span style={{ fontSize: "0.68rem", color: j.applied ? G.green : G.accent, background: j.applied ? G.greenSoft : G.accentSoft, border: `1px solid ${j.applied ? G.greenBorder : G.accentBorder}`, borderRadius: 20, padding: "2px 8px" }}>
              {j.applied ? "Applied" : "Pending"}
            </span>
          </div>
        ))
      }
    </div>
  );
}

function SkeletonCard() {
  return (
    <div style={{ background: G.b2, borderRadius: 16, padding: 20, marginBottom: 8, border: `1px solid ${G.border}` }}>
      {[[70, 14], [45, 10], [85, 10]].map(([w, mt], i) => (
        <div key={i} className="shimmer" style={{ height: 13, width: `${w}%`, borderRadius: 6, marginTop: mt }} />
      ))}
    </div>
  );
}

function JobCard({ job, onMarkApplied, onDelete, onTailor, index }) {
  return (
    <div className="job-card" style={{ animationDelay: `${index * 0.04}s`, borderLeft: `3px solid ${job.applied ? G.green : G.accent}`, borderRadius: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <p style={{ fontWeight: 700, fontFamily: "'Syne',sans-serif", fontSize: "0.95rem", color: G.t1, marginBottom: 3, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>{job.company_name}</p>
          <p style={{ fontSize: "0.82rem", color: G.accent }}>{job.role}</p>
        </div>
        <span style={{ fontSize: "0.65rem", borderRadius: 20, padding: "2px 9px", flexShrink: 0, marginLeft: 10, fontWeight: 500, background: job.applied ? G.greenSoft : G.accentSoft, color: job.applied ? G.green : G.accent, border: `1px solid ${job.applied ? G.greenBorder : G.accentBorder}` }}>
          {job.applied ? "✓ Applied" : "Pending"}
        </span>
      </div>
      <div style={{ display: "flex", flexWrap: "wrap", gap: 5, marginBottom: 8 }}>
        {[["📅", job.deadline], ["💰", job.stipend], ["🏢", job.work_format], ["📍", job.location]].filter(([, v]) => v).map(([icon, val]) => (
          <span key={val} style={{ fontSize: "0.73rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 6, padding: "2px 8px" }}>{icon} {val}</span>
        ))}
      </div>
      {job.ats_score !== null && job.ats_score !== undefined && (
        <span style={{ display: 'inline-block', fontSize: '0.7rem', fontWeight: 700, color: job.ats_score >= 70 ? G.green : job.ats_score >= 50 ? G.amber : G.red, background: job.ats_score >= 70 ? G.greenSoft : job.ats_score >= 50 ? G.amberSoft : G.redSoft, border: '1px solid ' + (job.ats_score >= 70 ? G.greenBorder : job.ats_score >= 50 ? G.amberBorder : G.red + '40'), borderRadius: 20, padding: '2px 9px', marginBottom: 8 }}>ATS {job.ats_score}%</span>
      )}
      {job.eligibility && <p style={{ fontSize: "0.75rem", color: G.t3, marginBottom: 4 }}>🎓 {job.eligibility}</p>}
      {job.extra_notes && <p style={{ fontSize: "0.73rem", color: G.t3, fontStyle: "italic", marginBottom: 8 }}>📝 {job.extra_notes}</p>}
      <div style={{ display: "flex", gap: 7, marginTop: 12, flexWrap: "wrap", alignItems: "center" }}>
        {job.apply_link && (
          <a href={job.apply_link} target="_blank" rel="noreferrer" style={{ background: G.accent, color: "#fff", padding: "6px 14px", borderRadius: 8, textDecoration: "none", fontSize: "0.78rem", fontWeight: 600 }}>Apply →</a>
        )}
        {!job.applied && (
          <button className="btn" onClick={() => onMarkApplied(job._id)} style={{ background: G.greenSoft, color: G.green, padding: "6px 12px", borderRadius: 8, border: `1px solid ${G.greenBorder}`, fontSize: "0.78rem" }}>Mark applied</button>
        )}
        <button className="btn" onClick={() => onDelete(job._id)} style={{ background: "transparent", color: G.t3, padding: "6px 10px", borderRadius: 8, border: `1px solid ${G.border}`, fontSize: "0.78rem", marginLeft: "auto" }}>✕</button>
      </div>
    </div>
  );
}

function LoginScreen({ onLogin }) {
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState("email");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const requestOtp = async () => {
    const val = email.trim();
    if (!val || !val.includes("@")) { setError("Enter a valid email address"); return; }
    setLoading(true); setError("");
    try {
      await axios.post(`${API_BASE}/auth/request-otp`, { phone: val });
      setStep("otp");
      setCountdown(60);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to send OTP. Try again.");
    } finally { setLoading(false); }
  };

  const verifyOtp = async () => {
    if (!otp.trim() || otp.length !== 6) { setError("Enter the 6-digit OTP"); return; }
    setLoading(true); setError("");
    try {
      const res = await axios.post(`${API_BASE}/auth/verify-otp`, { phone: email.trim(), otp: otp.trim() });
      localStorage.setItem("maitx_token", res.data.token);
      localStorage.setItem("maitx_user", res.data.user_id);
      onLogin(res.data.user_id);
    } catch (e) {
      setError(e.response?.data?.detail || "Invalid OTP. Try again.");
    } finally { setLoading(false); }
  };

  const inputStyle = {
    background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10,
    padding: "12px 14px", color: G.t1, fontSize: "0.95rem", width: "100%",
    marginBottom: 10, fontFamily: "'DM Sans',sans-serif",
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24, background: G.bg }}>
      <div style={{ width: "100%", maxWidth: 400, animation: "fadeUp 0.4s ease" }}>
        <div style={{ textAlign: "center", marginBottom: 40 }}>
          <p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", color: G.accent, textTransform: "uppercase", marginBottom: 12 }}>TnP Internship Tracker</p>
          <h1 style={{ fontSize: "3.5rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1, letterSpacing: "-0.02em" }}>MAITX</h1>
          <p style={{ color: G.t2, marginTop: 10, fontSize: "0.88rem" }}>AI-powered job tracking via WhatsApp</p>
        </div>
        <div style={{ background: G.b2, borderRadius: 20, padding: 28, border: `1px solid ${G.border}` }}>
          {step === "email" ? (
            <>
              <p style={{ color: G.t2, fontSize: "0.84rem", marginBottom: 16, textAlign: "center" }}>Enter your college email</p>
              <input type="email" placeholder="you@college.edu" value={email}
                onChange={e => setEmail(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") requestOtp(); }}
                style={inputStyle} />
              <button className="btn" onClick={requestOtp} disabled={loading}
                style={{ background: G.accent, color: "#fff", padding: "12px", borderRadius: 10, fontSize: "0.92rem", fontWeight: 600, width: "100%", fontFamily: "'DM Sans',sans-serif", opacity: loading ? 0.7 : 1 }}>
                {loading ? "Sending OTP…" : "Send OTP"}
              </button>
            </>
          ) : (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                <button className="btn" onClick={() => { setStep("email"); setError(""); setOtp(""); }}
                  style={{ background: "transparent", color: G.t3, padding: "4px 8px", borderRadius: 6, border: `1px solid ${G.border}`, fontSize: "0.78rem" }}>←</button>
                <p style={{ color: G.t2, fontSize: "0.84rem" }}>OTP sent to <span style={{ color: G.t1 }}>{email}</span></p>
              </div>
              <input type="number" placeholder="Enter 6-digit OTP" value={otp}
                onChange={e => setOtp(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") verifyOtp(); }}
                className={otp.length === 6 ? "otp-sent" : ""}
                style={{ ...inputStyle, letterSpacing: "0.2em", fontSize: "1.2rem", textAlign: "center" }} />
              <button className="btn" onClick={verifyOtp} disabled={loading}
                style={{ background: G.accent, color: "#fff", padding: "12px", borderRadius: 10, fontSize: "0.92rem", fontWeight: 600, width: "100%", fontFamily: "'DM Sans',sans-serif", opacity: loading ? 0.7 : 1 }}>
                {loading ? "Verifying…" : "Verify & Login"}
              </button>
              <div style={{ textAlign: "center", marginTop: 14 }}>
                {countdown > 0
                  ? <p style={{ color: G.t3, fontSize: "0.75rem" }}>Resend in {countdown}s</p>
                  : <button className="btn" onClick={requestOtp}
                      style={{ background: "transparent", color: G.accent, fontSize: "0.78rem", textDecoration: "underline", padding: 0 }}>
                      Resend OTP
                    </button>
                }
              </div>
            </>
          )}
          {error && (
            <div style={{ background: G.redSoft, border: `1px solid ${G.red}40`, borderRadius: 8, padding: "9px 12px", marginTop: 12, fontSize: "0.8rem", color: G.red }}>
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [userId, setUserId] = useState(getStoredUser() || "");
  const [activeTab, setActiveTab] = useState("jobs");
  const [prefilledJob, setPrefilledJob] = useState(null);
  const [activeTab, setActiveTab] = useState("jobs");

  useEffect(() => { injectStyles(); }, []);

  const handleLogout = () => {
    localStorage.removeItem("maitx_token");
    localStorage.removeItem("maitx_user");
    setUserId(""); setJobs([]); setLoading(true);
  };

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/jobs/${userId}`, authHeaders());
      setJobs(res.data);
    } catch (err) {
      if (err.response?.status === 401) handleLogout();
      console.error(err);
    } finally { setLoading(false); }
  }, [userId]);

  useEffect(() => { if (userId) fetchJobs(); }, [userId, fetchJobs]);

  useEffect(() => {
    if (!userId) return;
    const interval = setInterval(fetchJobs, 30000);
    return () => clearInterval(interval);
  }, [userId, fetchJobs]);

  const markApplied = async (id) => {
    await axios.patch(`${API_BASE}/api/jobs/${id}/applied`, {}, authHeaders());
    setJobs(jobs.map(j => j._id === id ? { ...j, applied: true } : j));
  };

  const deleteJob = async (id) => {
    await axios.delete(`${API_BASE}/api/jobs/${id}`, authHeaders());
    setJobs(jobs.filter(j => j._id !== id));
  };

  const filtered = jobs.filter(j => {
    const mf = filter === "applied" ? j.applied : filter === "pending" ? !j.applied : true;
    const ms = !search || [j.company_name, j.role, j.location].some(f => f?.toLowerCase().includes(search.toLowerCase()));
    return mf && ms;
  });

  if (window.location.pathname === "/admin") return <AdminPanel />;
  if (!userId) return <LoginScreen onLogin={setUserId} />;
  if (activeTab === "resume") return <ResumeTailor token={getToken()} prefilledJob={prefilledJob} onBack={() => { setActiveTab("jobs"); setPrefilledJob(null); }} />;

  const pending = jobs.filter(j => !j.applied).length;
  const applied = jobs.filter(j => j.applied).length;

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>Dashboard</p>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1, letterSpacing: "-0.02em" }}>MAITX</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn" onClick={fetchJobs} style={{ background: G.b2, color: G.t2, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", fontFamily: "'DM Sans',sans-serif" }}>↻</button>
          <button className="btn" onClick={handleLogout} style={{ background: "transparent", color: G.t3, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", fontFamily: "'DM Sans',sans-serif" }}>Logout</button>
        </div>
      </div>

      {/* Nav tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {[["jobs", "💼 Jobs"], ["resume", "✨ Tailor Resume"]].map(([id, label]) => (
          <button key={id} onClick={() => setActiveTab(id)}
            style={{ padding: "8px 18px", borderRadius: 10, border: `1px solid ${activeTab === id ? G.accent : G.border}`, background: activeTab === id ? G.accentSoft : "transparent", color: activeTab === id ? G.accent : G.t2, cursor: "pointer", fontSize: "0.84rem", fontFamily: "inherit", fontWeight: activeTab === id ? 600 : 400 }}>
            {label}
          </button>
        ))}
      </div>

      <div className="bento-grid">
        <BentoStat label="Total saved" value={jobs.length} color={G.accent} soft={G.accentSoft} />
        <BentoStat label="Pending" value={pending} color={G.amber} soft={G.amberSoft} sub={pending > 0 ? "Don't miss deadlines" : "All caught up!"} />
        <BentoStat label="Applied" value={applied} color={G.green} soft={G.greenSoft} />
      </div>
      <div className="bento-grid">
        <ApplyRateBox jobs={jobs} />
        <RecentActivity jobs={jobs} />
      </div>

      <div style={{ display: "flex", gap: 8, marginBottom: 16, flexWrap: "wrap", alignItems: "center" }}>
        <input type="text" placeholder="Search jobs..." value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 160, background: G.b2, border: `1px solid ${G.border}`, borderRadius: 10, padding: "8px 13px", color: G.t1, fontSize: "0.84rem", fontFamily: "'DM Sans',sans-serif" }} />
        <div style={{ display: "flex", gap: 6 }}>
          {["all", "pending", "applied"].map(f => (
            <button key={f} onClick={() => setFilter(f)} className={`filter-btn${filter === f ? " active" : ""}`}>
              {f.charAt(0).toUpperCase() + f.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {!loading && (
        <p style={{ fontSize: "0.73rem", color: G.t3, marginBottom: 12, letterSpacing: "0.04em" }}>
          {filtered.length} {filtered.length === 1 ? "job" : "jobs"}{filter !== "all" ? ` · ${filter}` : ""}{search ? ` · "${search}"` : ""}
        </p>
      )}

      {loading
        ? [1, 2, 3].map(i => <SkeletonCard key={i} />)
        : filtered.length === 0
          ? (
            <div style={{ textAlign: "center", padding: "50px 0", color: G.t3 }}>
              <p style={{ fontSize: "2rem", marginBottom: 12 }}>📭</p>
              <p style={{ fontSize: "0.9rem" }}>No jobs found</p>
              <p style={{ fontSize: "0.78rem", marginTop: 6 }}>Forward TnP messages to the WhatsApp bot to save jobs</p>
            </div>
          )
          : filtered.map((job, i) => (
            <JobCard key={job._id} job={job} index={i} onMarkApplied={markApplied} onDelete={deleteJob} onTailor={(job) => { setPrefilledJob(job); setActiveTab("resume"); }} />
          ))
      }
    </div>
  );
}
