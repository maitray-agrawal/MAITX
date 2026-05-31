import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_BASE = "https://web-production-c1e12.up.railway.app";

const theme = {
  bg: "#0a0a0f",
  surface: "#111118",
  card: "#16161f",
  cardHover: "#1c1c28",
  border: "#2a2a3a",
  borderAccent: "#3d3d55",
  accent: "#7c6af7",
  accentDim: "#7c6af722",
  accentBorder: "#7c6af744",
  green: "#34d399",
  greenDim: "#34d39918",
  greenBorder: "#34d39933",
  red: "#f87171",
  redDim: "#f8717118",
  redBorder: "#f8717133",
  amber: "#fbbf24",
  amberDim: "#fbbf2415",
  textPrimary: "#f0f0fa",
  textSecondary: "#8888aa",
  textMuted: "#555570",
};

const globalStyles = `
  @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: ${theme.bg}; color: ${theme.textPrimary}; font-family: 'DM Sans', sans-serif; }
  ::-webkit-scrollbar { width: 4px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: ${theme.border}; border-radius: 2px; }
  @keyframes fadeUp { from { opacity: 0; transform: translateY(16px); } to { opacity: 1; transform: translateY(0); } }
  @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.4; } }
  @keyframes shimmer { from { background-position: -200% 0; } to { background-position: 200% 0; } }
`;

function SkeletonCard() {
  return (
    <div style={{ background: theme.card, borderRadius: 16, padding: 24, marginBottom: 12, border: `1px solid ${theme.border}` }}>
      {[["60%", 14], ["40%", 12], ["80%", 10]].map(([w, mt], i) => (
        <div key={i} style={{
          height: 14, width: w, borderRadius: 7, marginTop: mt,
          background: `linear-gradient(90deg, ${theme.border} 25%, ${theme.borderAccent} 50%, ${theme.border} 75%)`,
          backgroundSize: "200% 100%",
          animation: `shimmer 1.5s infinite ${i * 0.2}s`
        }} />
      ))}
    </div>
  );
}

function StatCard({ num, label, color, icon }) {
  return (
    <div style={{
      flex: 1, background: theme.card, borderRadius: 16, padding: "20px 16px",
      border: `1px solid ${theme.border}`, textAlign: "center", position: "relative", overflow: "hidden"
    }}>
      <div style={{
        position: "absolute", top: -20, right: -20, width: 80, height: 80,
        borderRadius: "50%", background: color + "15"
      }} />
      <div style={{ fontSize: 28, marginBottom: 4 }}>{icon}</div>
      <div style={{ fontSize: "1.8rem", fontWeight: 700, color, fontFamily: "'Syne', sans-serif", lineHeight: 1 }}>{num}</div>
      <div style={{ fontSize: "0.78rem", color: theme.textMuted, marginTop: 6, letterSpacing: "0.08em", textTransform: "uppercase" }}>{label}</div>
    </div>
  );
}

function JobCard({ job, onMarkApplied, onDelete, index }) {
  const [hovering, setHovering] = useState(false);
  const [deleting, setDeleting] = useState(false);

  const handleDelete = async () => {
    setDeleting(true);
    await onDelete(job._id);
  };

  return (
    <div
      onMouseEnter={() => setHovering(true)}
      onMouseLeave={() => setHovering(false)}
      style={{
        background: hovering ? theme.cardHover : theme.card,
        borderRadius: 16,
        padding: "20px 24px",
        marginBottom: 12,
        border: `1px solid ${hovering ? theme.borderAccent : theme.border}`,
        borderLeft: `3px solid ${job.applied ? theme.green : theme.accent}`,
        transition: "all 0.2s ease",
        animation: `fadeUp 0.3s ease ${index * 0.05}s both`,
        opacity: deleting ? 0.4 : 1,
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 4 }}>
            <h3 style={{ fontSize: "1rem", fontWeight: 600, fontFamily: "'Syne', sans-serif", color: theme.textPrimary, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {job.company_name}
            </h3>
            {job.applied && (
              <span style={{ fontSize: "0.65rem", background: theme.greenDim, color: theme.green, border: `1px solid ${theme.greenBorder}`, borderRadius: 20, padding: "2px 8px", whiteSpace: "nowrap", fontWeight: 500 }}>
                ✓ Applied
              </span>
            )}
          </div>
          <p style={{ fontSize: "0.88rem", color: theme.accent, fontWeight: 500 }}>{job.role}</p>
        </div>
        {!job.applied && (
          <span style={{ fontSize: "0.65rem", background: theme.accentDim, color: theme.accent, border: `1px solid ${theme.accentBorder}`, borderRadius: 20, padding: "2px 8px", whiteSpace: "nowrap", fontWeight: 500 }}>
            Pending
          </span>
        )}
      </div>

      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginBottom: 10 }}>
        {job.deadline && <Chip icon="📅" text={job.deadline} />}
        {job.stipend && <Chip icon="💰" text={job.stipend} />}
        {job.work_format && <Chip icon="🏢" text={job.work_format} />}
        {job.location && <Chip icon="📍" text={job.location} />}
      </div>

      {job.eligibility && (
        <p style={{ fontSize: "0.78rem", color: theme.textSecondary, marginBottom: 6, display: "flex", alignItems: "center", gap: 6 }}>
          <span>🎓</span> {job.eligibility}
        </p>
      )}
      {job.extra_notes && (
        <p style={{ fontSize: "0.75rem", color: theme.textMuted, marginBottom: 10, fontStyle: "italic" }}>
          📝 {job.extra_notes}
        </p>
      )}

      <div style={{ display: "flex", gap: 8, marginTop: 14, flexWrap: "wrap" }}>
        {job.apply_link && (
          <a href={job.apply_link} target="_blank" rel="noreferrer" style={{
            background: theme.accent, color: "#fff", padding: "7px 16px",
            borderRadius: 8, textDecoration: "none", fontSize: "0.82rem", fontWeight: 600,
            letterSpacing: "0.02em", transition: "opacity 0.15s"
          }}>
            Apply Now →
          </a>
        )}
        {!job.applied && (
          <button onClick={() => onMarkApplied(job._id)} style={{
            background: theme.greenDim, color: theme.green, padding: "7px 14px",
            borderRadius: 8, border: `1px solid ${theme.greenBorder}`, cursor: "pointer",
            fontSize: "0.82rem", fontWeight: 500
          }}>
            Mark Applied
          </button>
        )}
        <button onClick={handleDelete} style={{
          background: "transparent", color: theme.textMuted, padding: "7px 12px",
          borderRadius: 8, border: `1px solid ${theme.border}`, cursor: "pointer",
          fontSize: "0.82rem", marginLeft: "auto"
        }}>
          ✕
        </button>
      </div>
    </div>
  );
}

function Chip({ icon, text }) {
  return (
    <span style={{
      background: "#1e1e2e", color: theme.textSecondary, padding: "3px 10px",
      borderRadius: 6, fontSize: "0.75rem", border: `1px solid ${theme.border}`,
      display: "flex", alignItems: "center", gap: 4
    }}>
      <span style={{ fontSize: "0.7rem" }}>{icon}</span> {text}
    </span>
  );
}

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [search, setSearch] = useState("");
  const [userId, setUserId] = useState(localStorage.getItem("maitx_user") || "");
  const [inputNumber, setInputNumber] = useState("");

  const fetchJobs = useCallback(async () => {
    setLoading(true);
    try {
      const res = await axios.get(`${API_BASE}/api/jobs/${userId}`);
      setJobs(res.data);
    } catch (err) {
      console.error("Error fetching jobs:", err);
    } finally {
      setLoading(false);
    }
  }, [userId]);

  useEffect(() => {
    if (userId) fetchJobs();
  }, [userId, fetchJobs]);

  const handleLogin = () => {
    const val = inputNumber.trim();
    if (val) { localStorage.setItem("maitx_user", val); setUserId(val); }
  };

  const handleLogout = () => {
    localStorage.removeItem("maitx_user");
    setUserId(""); setJobs([]); setLoading(true);
  };

  const markApplied = async (jobId) => {
    await axios.patch(`${API_BASE}/api/jobs/${jobId}/applied`);
    setJobs(jobs.map(j => j._id === jobId ? { ...j, applied: true } : j));
  };

  const deleteJob = async (jobId) => {
    await axios.delete(`${API_BASE}/api/jobs/${jobId}`);
    setJobs(jobs.filter(j => j._id !== jobId));
  };

  const filtered = jobs.filter(j => {
    const matchFilter = filter === "applied" ? j.applied : filter === "pending" ? !j.applied : true;
    const matchSearch = !search || [j.company_name, j.role, j.location].some(f => f?.toLowerCase().includes(search.toLowerCase()));
    return matchFilter && matchSearch;
  });

  if (!userId) {
    return (
      <>
        <style>{globalStyles}</style>
        <div style={{ minHeight: "100vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "24px 16px", background: theme.bg }}>
          <div style={{ position: "fixed", top: "20%", left: "50%", transform: "translateX(-50%)", width: 600, height: 600, borderRadius: "50%", background: `radial-gradient(circle, ${theme.accent}08 0%, transparent 70%)`, pointerEvents: "none" }} />
          <div style={{ textAlign: "center", marginBottom: 48, animation: "fadeUp 0.5s ease" }}>
            <div style={{ fontSize: "0.72rem", letterSpacing: "0.2em", color: theme.accent, textTransform: "uppercase", marginBottom: 16, fontWeight: 500 }}>
              TnP Internship Tracker
            </div>
            <h1 style={{ fontSize: "4rem", fontWeight: 800, fontFamily: "'Syne', sans-serif", color: theme.textPrimary, letterSpacing: "-0.02em", lineHeight: 1 }}>
              MAITX
            </h1>
            <p style={{ color: theme.textSecondary, marginTop: 12, fontSize: "0.95rem" }}>
              Forward TnP messages → AI extracts → Dashboard tracks
            </p>
          </div>

          <div style={{
            background: theme.card, borderRadius: 20, padding: 32, width: "100%", maxWidth: 400,
            border: `1px solid ${theme.border}`, animation: "fadeUp 0.5s ease 0.1s both"
          }}>
            <p style={{ color: theme.textSecondary, marginBottom: 20, fontSize: "0.88rem", textAlign: "center" }}>
              Enter your WhatsApp number to access your jobs
            </p>
            <input
              type="tel"
              placeholder="91XXXXXXXXXX"
              value={inputNumber}
              onChange={(e) => setInputNumber(e.target.value)}
              onKeyDown={(e) => { if (e.key === "Enter") handleLogin(); }}
              style={{
                background: "#0f0f18", border: `1px solid ${theme.border}`, borderRadius: 10,
                padding: "13px 16px", color: theme.textPrimary, fontSize: "1rem", width: "100%",
                outline: "none", marginBottom: 12, fontFamily: "'DM Sans', sans-serif",
                transition: "border-color 0.2s"
              }}
              onFocus={e => e.target.style.borderColor = theme.accent}
              onBlur={e => e.target.style.borderColor = theme.border}
            />
            <button onClick={handleLogin} style={{
              background: theme.accent, color: "#fff", padding: "13px 24px", borderRadius: 10,
              border: "none", cursor: "pointer", fontWeight: 600, fontSize: "0.95rem", width: "100%",
              fontFamily: "'DM Sans', sans-serif", letterSpacing: "0.02em", transition: "opacity 0.15s"
            }}
              onMouseEnter={e => e.target.style.opacity = "0.85"}
              onMouseLeave={e => e.target.style.opacity = "1"}
            >
              View My Jobs
            </button>
            <p style={{ color: theme.textMuted, fontSize: "0.72rem", textAlign: "center", marginTop: 16 }}>
              Include country code · e.g. 91XXXXXXXXXX for India
            </p>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <style>{globalStyles}</style>
      <div style={{ minHeight: "100vh", background: theme.bg, padding: "24px 16px", maxWidth: 760, margin: "0 auto" }}>

        {/* Header */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 40 }}>
          <div>
            <div style={{ fontSize: "0.68rem", letterSpacing: "0.18em", color: theme.accent, textTransform: "uppercase", marginBottom: 4 }}>
              TnP Tracker
            </div>
            <h1 style={{ fontSize: "2.2rem", fontWeight: 800, fontFamily: "'Syne', sans-serif", color: theme.textPrimary, letterSpacing: "-0.02em", lineHeight: 1 }}>
              MAITX
            </h1>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <button onClick={fetchJobs} style={{
              background: "transparent", color: theme.textSecondary, border: `1px solid ${theme.border}`,
              borderRadius: 8, padding: "7px 14px", cursor: "pointer", fontSize: "0.82rem"
            }}>
              ↻ Refresh
            </button>
            <button onClick={handleLogout} style={{
              background: "transparent", color: theme.textMuted, border: `1px solid ${theme.border}`,
              borderRadius: 8, padding: "7px 14px", cursor: "pointer", fontSize: "0.82rem"
            }}>
              Logout
            </button>
          </div>
        </div>

        {/* Stats */}
        <div style={{ display: "flex", gap: 12, marginBottom: 28 }}>
          <StatCard num={jobs.length} label="Total" color={theme.accent} icon="📋" />
          <StatCard num={jobs.filter(j => !j.applied).length} label="Pending" color={theme.amber} icon="⏳" />
          <StatCard num={jobs.filter(j => j.applied).length} label="Applied" color={theme.green} icon="✅" />
        </div>

        {/* Search + Filter */}
        <div style={{ display: "flex", gap: 10, marginBottom: 24, flexWrap: "wrap" }}>
          <input
            type="text"
            placeholder="Search company, role, location..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              flex: 1, minWidth: 200, background: theme.card, border: `1px solid ${theme.border}`,
              borderRadius: 10, padding: "9px 14px", color: theme.textPrimary, fontSize: "0.88rem",
              outline: "none", fontFamily: "'DM Sans', sans-serif"
            }}
            onFocus={e => e.target.style.borderColor = theme.accent}
            onBlur={e => e.target.style.borderColor = theme.border}
          />
          <div style={{ display: "flex", gap: 6 }}>
            {["all", "pending", "applied"].map(f => (
              <button key={f} onClick={() => setFilter(f)} style={{
                padding: "9px 18px", borderRadius: 10, border: `1px solid ${filter === f ? theme.accent : theme.border}`,
                background: filter === f ? theme.accentDim : "transparent",
                color: filter === f ? theme.accent : theme.textSecondary,
                cursor: "pointer", fontSize: "0.82rem", fontWeight: filter === f ? 600 : 400,
                transition: "all 0.15s", fontFamily: "'DM Sans', sans-serif"
              }}>
                {f.charAt(0).toUpperCase() + f.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Results count */}
        {!loading && (
          <p style={{ fontSize: "0.78rem", color: theme.textMuted, marginBottom: 16, letterSpacing: "0.05em" }}>
            {filtered.length} {filtered.length === 1 ? "job" : "jobs"} {filter !== "all" ? `· ${filter}` : ""}{search ? ` · "${search}"` : ""}
          </p>
        )}

        {/* Job list */}
        {loading ? (
          [1, 2, 3].map(i => <SkeletonCard key={i} />)
        ) : filtered.length === 0 ? (
          <div style={{ textAlign: "center", padding: "60px 0", color: theme.textMuted }}>
            <div style={{ fontSize: "2.5rem", marginBottom: 16 }}>📭</div>
            <p style={{ fontSize: "0.95rem" }}>No jobs found</p>
            <p style={{ fontSize: "0.8rem", marginTop: 6 }}>Forward TnP messages to the bot to save jobs</p>
          </div>
        ) : (
          filtered.map((job, i) => (
            <JobCard key={job._id} job={job} index={i} onMarkApplied={markApplied} onDelete={deleteJob} />
          ))
        )}
      </div>
    </>
  );
}

export default App;