import { useState, useEffect, useCallback } from "react";
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
  `;
  document.head.appendChild(s);
};

// ── auth helpers ──────────────────────────────────────────────
const getToken = () => localStorage.getItem("maitx_token");
const getStoredUser = () => localStorage.getItem("maitx_user");

const authHeaders = () => ({
  headers: { Authorization: `Bearer ${getToken()}` }
});

// ── sub-components (unchanged) ────────────────────────────────
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

function JobCard({ job, onMarkApplied, onDelete, index }) {
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

// ── Login screen with OTP flow ────────────────────────────────
function LoginScreen({ onLogin }) {
  const [phone, setPhone] = useState("");
  const [otp, setOtp] = useState("");
  const [step, setStep] = useState("phone"); // "phone" | "otp"
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [countdown, setCountdown] = useState(0);

  useEffect(() => {
    if (countdown <= 0) return;
    const t = setTimeout(() => setCountdown(c => c - 1), 1000);
    return () => clearTimeout(t);
  }, [countdown]);

  const requestOtp = async () => {
    const val = phone.trim();
    if (!val || val.length < 10) { setError("Enter a valid number with country code"); return; }
    setLoading(true); setError("");
    try {
      await axios.post(`${API_BASE}/auth/request-otp`, { phone: val });
      setStep("otp");
      setCountdown(60);
    } catch (e) {
      setError(e.response?.data?.detail || "Failed to send OTP. Try again.");
    } finally {
      setLoading(false);
    }
  };

  const verifyOtp = async () => {
    if (!otp.trim() || otp.length !== 6) { setError("Enter the 6-digit OTP"); return; }
    setLoading(true); setError("");
    try {
      const res = await axios.post(`${API_BASE}/auth/verify-otp`, { phone: phone.trim(), otp: otp.trim() });
      localStorage.setItem("maitx_token", res.data.token);
      localStorage.setItem("maitx_user", res.data.user_id);
      onLogin(res.data.user_id);
    } catch (e) {
      setError(e.response?.data?.detail || "Invalid OTP. Try again.");
    } finally {
      setLoading(false);
    }
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
          {step === "phone" ? (
            <>
              <p style={{ color: G.t2, fontSize: "0.84rem", marginBottom: 16, textAlign: "center" }}>Enter your WhatsApp number</p>
              <input
                type="email" placeholder="you@gmail.com" value={phone}
                onChange={e => setPhone(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") requestOtp(); }}
                style={inputStyle}
              />
              <button className="btn" onClick={requestOtp} disabled={loading}
                style={{ background: G.accent, color: "#fff", padding: "12px", borderRadius: 10, fontSize: "0.92rem", fontWeight: 600, width: "100%", fontFamily: "'DM Sans',sans-serif", opacity: loading ? 0.7 : 1 }}>
                {loading ? "Sending OTP…" : "Send OTP via Email"}
              </button>
              <p style={{ color: G.t3, fontSize: "0.7rem", textAlign: "center", marginTop: 14 }}>Enter email to receive OTP · 91XXXXXXXXXX for India</p>
            </>
          ) : (
            <>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
                <button className="btn" onClick={() => { setStep("phone"); setError(""); setOtp(""); }}
                  style={{ background: "transparent", color: G.t3, padding: "4px 8px", borderRadius: 6, border: `1px solid ${G.border}`, fontSize: "0.78rem" }}>←</button>
                <p style={{ color: G.t2, fontSize: "0.84rem" }}>OTP sent to <span style={{ color: G.t1 }}>+{phone}</span></p>
              </div>
              <div style={{ background: G.accentSoft, border: `1px solid ${G.accentBorder}`, borderRadius: 10, padding: "10px 14px", marginBottom: 14, fontSize: "0.8rem", color: G.accent }}>
                📧 Check your email inbox for the 6-digit code
              </div>
              <input
                type="number" placeholder="Enter 6-digit OTP" value={otp}
                onChange={e => setOtp(e.target.value)}
                onKeyDown={e => { if (e.key === "Enter") verifyOtp(); }}
                className={otp.length === 6 ? "otp-sent" : ""}
                style={{ ...inputStyle, letterSpacing: "0.2em", fontSize: "1.2rem", textAlign: "center" }}
              />
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

// ── Main app ──────────────────────────────────────────────────
export default function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [userId, setUserId] = useState(getStoredUser() || "");

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
      // Token expired or invalid — force logout
      if (err.response?.status === 401) handleLogout();
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [userId]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => { if (userId) fetchJobs(); }, [userId, fetchJobs]);

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

  if (window.location.pathname === "/admin") {
  return <AdminPanel />;
}

if (!userId) {
  return <LoginScreen onLogin={setUserId} />;
}

  const pending = jobs.filter(j => !j.applied).length;
  const applied = jobs.filter(j => j.applied).length;

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 820, margin: "0 auto" }}>

      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>Dashboard</p>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1, letterSpacing: "-0.02em" }}>MAITX</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button className="btn" onClick={fetchJobs} style={{ background: G.b2, color: G.t2, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", fontFamily: "'DM Sans',sans-serif" }}>↻</button>
          <button className="btn" onClick={handleLogout} style={{ background: "transparent", color: G.t3, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", fontFamily: "'DM Sans',sans-serif" }}>Logout</button>
        </div>
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
        <input
          type="text" placeholder="Search jobs..." value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ flex: 1, minWidth: 160, background: G.b2, border: `1px solid ${G.border}`, borderRadius: 10, padding: "8px 13px", color: G.t1, fontSize: "0.84rem", fontFamily: "'DM Sans',sans-serif" }}
        />
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
            <JobCard key={job._id} job={job} index={i} onMarkApplied={markApplied} onDelete={deleteJob} />
          ))
      }
    </div>
  );
}