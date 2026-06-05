import { useState, useEffect } from "react";
import axios from "axios";

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

export default function AdminPanel() {
  const [secret, setSecret] = useState("");
  const [token, setToken] = useState(localStorage.getItem("maitx_admin_token") || "");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [loginLoading, setLoginLoading] = useState(false);

  const authHeaders = () => ({ headers: { Authorization: `Bearer ${token}` } });

  const login = async () => {
    setLoginLoading(true); setError("");
    try {
      const res = await axios.post(`${API_BASE}/admin/login`, { secret });
      localStorage.setItem("maitx_admin_token", res.data.token);
      setToken(res.data.token);
    } catch {
      setError("Invalid admin secret");
    } finally {
      setLoginLoading(false);
    }
  };

  const logout = () => {
    localStorage.removeItem("maitx_admin_token");
    setToken(""); setStats(null); setUsers([]); setJobs([]);
  };

  const fetchData = async () => {
    setLoading(true);
    try {
      const [statsRes, usersRes, jobsRes] = await Promise.all([
        axios.get(`${API_BASE}/admin/stats`, authHeaders()),
        axios.get(`${API_BASE}/admin/users`, authHeaders()),
        axios.get(`${API_BASE}/admin/jobs?limit=100`, authHeaders()),
      ]);
      setStats(statsRes.data);
      setUsers(usersRes.data.users);
      setJobs(jobsRes.data);
    } catch (e) {
      if (e.response?.status === 403) { logout(); }
    } finally {
      setLoading(false);
    }
  };

  const deleteJob = async (id) => {
    await axios.delete(`${API_BASE}/admin/jobs/${id}`, authHeaders());
    setJobs(jobs.filter(j => j._id !== id));
  };

  useEffect(() => { if (token) fetchData(); }, [token]);

  const card = (children, extra = {}) => (
    <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}`, ...extra }}>
      {children}
    </div>
  );

  const label = (text) => (
    <p style={{ fontSize: "0.68rem", letterSpacing: "0.12em", color: G.t3, textTransform: "uppercase", marginBottom: 10 }}>{text}</p>
  );

  if (!token) {
    return (
      <div style={{ minHeight: "100vh", background: G.bg, display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
        <div style={{ width: "100%", maxWidth: 380 }}>
          <div style={{ textAlign: "center", marginBottom: 36 }}>
            <p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", color: G.accent, textTransform: "uppercase", marginBottom: 10 }}>Admin Access</p>
            <h1 style={{ fontSize: "2.8rem", fontWeight: 800, fontFamily: "sans-serif", color: G.t1 }}>MAITX</h1>
          </div>
          {card(<>
            {label("Admin Secret")}
            <input
              type="password" value={secret} onChange={e => setSecret(e.target.value)}
              onKeyDown={e => { if (e.key === "Enter") login(); }}
              placeholder="Enter admin secret"
              style={{ width: "100%", background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10, padding: "11px 14px", color: G.t1, fontSize: "0.92rem", fontFamily: "sans-serif", marginBottom: 12 }}
            />
            {error && <p style={{ color: G.red, fontSize: "0.8rem", marginBottom: 10 }}>{error}</p>}
            <button onClick={login} disabled={loginLoading}
              style={{ width: "100%", background: G.accent, color: "#fff", border: "none", borderRadius: 10, padding: "11px", fontSize: "0.92rem", fontWeight: 600, cursor: "pointer", opacity: loginLoading ? 0.7 : 1 }}>
              {loginLoading ? "Logging in..." : "Login"}
            </button>
          </>)}
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 900, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.accent, textTransform: "uppercase", marginBottom: 4 }}>Admin Panel</p>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, fontFamily: "sans-serif", color: G.t1 }}>MAITX Control</h1>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={fetchData} style={{ background: G.b2, color: G.t2, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", cursor: "pointer" }}>↻ Refresh</button>
          <button onClick={logout} style={{ background: "transparent", color: G.t3, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", cursor: "pointer" }}>Logout</button>
        </div>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 6, marginBottom: 24 }}>
        {["overview", "users", "jobs"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "7px 18px", borderRadius: 9, border: `1px solid ${tab === t ? G.accent : G.border}`, background: tab === t ? G.accentSoft : "transparent", color: tab === t ? G.accent : G.t2, fontSize: "0.82rem", cursor: "pointer", fontWeight: tab === t ? 600 : 400 }}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {loading && <p style={{ color: G.t3, fontSize: "0.85rem" }}>Loading...</p>}

      {/* Overview Tab */}
      {!loading && tab === "overview" && stats && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10, marginBottom: 10 }}>
            {[
              ["Total Users", stats.total_users, G.accent, G.accentSoft],
              ["Total Jobs", stats.total_jobs, G.amber, G.amberSoft],
              ["Applied", stats.total_applied, G.green, G.greenSoft],
            ].map(([lbl, val, color, soft]) => (
              <div key={lbl} style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}`, position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", bottom: -16, right: -16, width: 64, height: 64, borderRadius: "50%", background: soft }} />
                {label(lbl)}
                <p style={{ fontSize: "2.4rem", fontWeight: 800, fontFamily: "sans-serif", color }}>{val}</p>
              </div>
            ))}
          </div>
          {card(<>
            {label("Apply Rate")}
            <p style={{ fontSize: "2rem", fontWeight: 800, color: G.green, marginBottom: 10 }}>{stats.apply_rate}%</p>
            <div style={{ display: "flex", gap: 4 }}>
              {Array.from({ length: 10 }).map((_, i) => (
                <div key={i} style={{ flex: 1, height: 6, borderRadius: 3, background: i < Math.round(stats.apply_rate / 10) ? G.green : G.border }} />
              ))}
            </div>
          </>)}
        </>
      )}

      {/* Users Tab */}
      {!loading && tab === "users" && (
        <>
          <p style={{ fontSize: "0.78rem", color: G.t3, marginBottom: 14 }}>{users.length} users on platform</p>
          {users.map(u => (
            <div key={u.user_id} style={{ background: G.b2, borderRadius: 14, padding: "16px 20px", marginBottom: 8, border: `1px solid ${G.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 8 }}>
                <p style={{ fontWeight: 600, color: G.t1, fontSize: "0.9rem" }}>{u.user_id}</p>
                <span style={{ fontSize: "0.68rem", color: G.t3 }}>
                  Last active: {u.last_active ? new Date(u.last_active).toLocaleDateString() : "—"}
                </span>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                <span style={{ fontSize: "0.73rem", color: G.accent, background: G.accentSoft, border: `1px solid ${G.accentBorder}`, borderRadius: 6, padding: "2px 8px" }}>
                  {u.total_jobs} jobs saved
                </span>
                <span style={{ fontSize: "0.73rem", color: G.green, background: G.greenSoft, border: `1px solid ${G.greenBorder}`, borderRadius: 6, padding: "2px 8px" }}>
                  {u.applied} applied
                </span>
                <span style={{ fontSize: "0.73rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 6, padding: "2px 8px" }}>
                  {u.total_jobs > 0 ? Math.round(u.applied / u.total_jobs * 100) : 0}% rate
                </span>
              </div>
            </div>
          ))}
        </>
      )}

      {/* Jobs Tab */}
      {!loading && tab === "jobs" && (
        <>
          <p style={{ fontSize: "0.78rem", color: G.t3, marginBottom: 14 }}>{jobs.length} jobs across all users</p>
          {jobs.map(j => (
            <div key={j._id} style={{ background: G.b2, borderRadius: 14, padding: "14px 18px", marginBottom: 8, border: `1px solid ${G.border}` }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
                <div style={{ flex: 1 }}>
                  <p style={{ fontWeight: 600, color: G.t1, fontSize: "0.88rem", marginBottom: 2 }}>{j.company_name} — <span style={{ color: G.accent }}>{j.role}</span></p>
                  <p style={{ fontSize: "0.72rem", color: G.t3, marginBottom: 6 }}>User: {j.user_id}</p>
                  <div style={{ display: "flex", gap: 6, flexWrap: "wrap" }}>
                    {j.deadline && <span style={{ fontSize: "0.7rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 5, padding: "1px 7px" }}>📅 {j.deadline}</span>}
                    {j.location && <span style={{ fontSize: "0.7rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 5, padding: "1px 7px" }}>📍 {j.location}</span>}
                    <span style={{ fontSize: "0.7rem", color: j.applied ? G.green : G.amber, background: j.applied ? G.greenSoft : G.amberSoft, border: `1px solid ${j.applied ? G.greenBorder : G.border}`, borderRadius: 5, padding: "1px 7px" }}>
                      {j.applied ? "✓ Applied" : "Pending"}
                    </span>
                  </div>
                </div>
                <button onClick={() => deleteJob(j._id)}
                  style={{ background: "transparent", color: G.t3, border: `1px solid ${G.border}`, borderRadius: 7, padding: "4px 9px", fontSize: "0.75rem", cursor: "pointer", marginLeft: 10, flexShrink: 0 }}>✕</button>
              </div>
            </div>
          ))}
        </>
      )}
    </div>
  );
}
