import { useState, useEffect } from "react";
import axios from "axios";

const API_BASE = "https://web-production-c1e12.up.railway.app";

const G = {
  bg: "#080810", b1: "#0f0f1a", b2: "#14141f", b3: "#1a1a28",
  border: "#25253a", borderHi: "#35355a",
  accent: "#7c6af7", accentSoft: "#7c6af712", accentBorder: "#7c6af740",
  green: "#34d399", greenSoft: "#34d39912", greenBorder: "#34d39930",
  amber: "#fbbf24", amberSoft: "#fbbf2412", amberBorder: "#fbbf2430",
  red: "#f87171", redSoft: "#f8717112",
  t1: "#eeeef8", t2: "#8888aa", t3: "#44445a",
};

const authH = (token) => ({ headers: { Authorization: `Bearer ${token}` } });

function StatCard({ label, value, color, soft }) {
  return (
    <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}`, position: "relative", overflow: "hidden" }}>
      <div style={{ position: "absolute", bottom: -16, right: -16, width: 64, height: 64, borderRadius: "50%", background: soft }} />
      <p style={{ fontSize: "0.68rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 10 }}>{label}</p>
      <p style={{ fontSize: "2.2rem", fontWeight: 800, fontFamily: "sans-serif", color, lineHeight: 1 }}>{value}</p>
    </div>
  );
}

export default function AdminPanel() {
  const [token, setToken] = useState(localStorage.getItem("maitx_admin_token") || "");
  const [secret, setSecret] = useState("");
  const [tab, setTab] = useState("overview");
  const [stats, setStats] = useState(null);
  const [users, setUsers] = useState({ users: [], total: 0, active: 0, inactive: 0 });
  const [companies, setCompanies] = useState([]);
  const [jobs, setJobs] = useState([]);
  const [broadcast, setBroadcast] = useState({ message: "", target: "all" });
  const [broadcastResult, setBroadcastResult] = useState(null);
  const [broadcastLoading, setBroadcastLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const login = async () => {
    setLoading(true); setError("");
    try {
      const r = await axios.post(`${API_BASE}/admin/login`, { secret });
      localStorage.setItem("maitx_admin_token", r.data.token);
      setToken(r.data.token);
    } catch (e) {
      setError(e.response?.data?.detail || "Invalid secret");
    } finally { setLoading(false); }
  };

  const logout = () => {
    localStorage.removeItem("maitx_admin_token");
    setToken(""); setStats(null);
  };

  useEffect(() => {
    if (!token) return;
    const h = authH(token);
    axios.get(`${API_BASE}/admin/stats`, h).then(r => setStats(r.data)).catch(logout);
    axios.get(`${API_BASE}/admin/users`, h).then(r => setUsers(r.data)).catch(() => {});
    axios.get(`${API_BASE}/admin/companies`, h).then(r => setCompanies(r.data.companies)).catch(() => {});
    axios.get(`${API_BASE}/admin/jobs`, h).then(r => setJobs(r.data)).catch(() => {});
  }, [token]);

  const deleteJob = async (id) => {
    await axios.delete(`${API_BASE}/admin/jobs/${id}`, authH(token));
    setJobs(jobs.filter(j => j._id !== id));
  };

  const sendBroadcast = async () => {
    if (!broadcast.message.trim()) return;
    setBroadcastLoading(true); setBroadcastResult(null);
    try {
      const r = await axios.post(`${API_BASE}/admin/broadcast`, broadcast, authH(token));
      setBroadcastResult(r.data);
    } catch (e) {
      setBroadcastResult({ error: e.response?.data?.detail || "Failed" });
    } finally { setBroadcastLoading(false); }
  };

  const TABS = ["overview", "users", "companies", "jobs", "broadcast"];

  if (!token) return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: G.bg, padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 380 }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", color: G.red, textTransform: "uppercase", marginBottom: 8 }}>Admin Access</p>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, color: G.t1 }}>MAITX</h1>
        </div>
        <div style={{ background: G.b2, borderRadius: 20, padding: 28, border: `1px solid ${G.border}` }}>
          <input type="password" placeholder="Admin secret" value={secret}
            onChange={e => setSecret(e.target.value)} onKeyDown={e => e.key === "Enter" && login()}
            style={{ width: "100%", background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10, padding: "12px 14px", color: G.t1, fontSize: "0.95rem", fontFamily: "inherit", marginBottom: 12, boxSizing: "border-box" }} />
          <button onClick={login} disabled={loading}
            style={{ width: "100%", background: G.red, color: "#fff", padding: 12, borderRadius: 10, border: "none", fontSize: "0.92rem", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}>
            {loading ? "Verifying…" : "Login as Admin"}
          </button>
          {error && <p style={{ color: G.red, fontSize: "0.8rem", marginTop: 10, textAlign: "center" }}>{error}</p>}
        </div>
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 960, margin: "0 auto" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.red, textTransform: "uppercase", marginBottom: 4 }}>Admin Panel</p>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: G.t1 }}>MAITX</h1>
        </div>
        <button onClick={logout} style={{ background: "transparent", color: G.t3, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", cursor: "pointer", fontFamily: "inherit" }}>Logout</button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24, flexWrap: "wrap" }}>
        {TABS.map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "7px 18px", borderRadius: 9, border: `1px solid ${tab === t ? G.accent : G.border}`, background: tab === t ? G.accentSoft : "transparent", color: tab === t ? G.accent : G.t2, cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit", fontWeight: tab === t ? 600 : 400 }}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Overview */}
      {tab === "overview" && stats && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginBottom: 10 }}>
            <StatCard label="Total Jobs" value={stats.total_jobs} color={G.accent} soft={G.accentSoft} />
            <StatCard label="Total Users" value={stats.total_users} color={G.amber} soft={G.amberSoft} />
            <StatCard label="Apply Rate" value={`${stats.apply_rate}%`} color={G.green} soft={G.greenSoft} />
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 10, marginBottom: 10 }}>
            <StatCard label="Active Users (7d)" value={users.active} color={G.green} soft={G.greenSoft} />
            <StatCard label="Inactive Users" value={users.inactive} color={G.red} soft={G.redSoft} />
          </div>
          {/* Top companies */}
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            <p style={{ fontSize: "0.68rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 14 }}>Top Companies</p>
            {(stats.top_companies || []).map((c, i) => (
              <div key={c.company} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "9px 0", borderBottom: i < stats.top_companies.length - 1 ? `1px solid ${G.border}` : "none" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                  <span style={{ fontSize: "0.72rem", color: G.t3, width: 20 }}>#{i + 1}</span>
                  <span style={{ fontSize: "0.85rem", color: G.t1 }}>{c.company || "Unknown"}</span>
                </div>
                <span style={{ fontSize: "0.78rem", color: G.accent, background: G.accentSoft, border: `1px solid ${G.accentBorder}`, borderRadius: 20, padding: "2px 10px" }}>{c.count} jobs</span>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Users */}
      {tab === "users" && (
        <>
          <div style={{ display: "flex", gap: 10, marginBottom: 14 }}>
            {[["Total", users.total, G.accent], ["Active 7d", users.active, G.green], ["Inactive", users.inactive, G.red]].map(([l, v, c]) => (
              <div key={l} style={{ background: G.b2, borderRadius: 12, padding: "12px 18px", border: `1px solid ${G.border}`, flex: 1, textAlign: "center" }}>
                <p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", marginBottom: 6 }}>{l}</p>
                <p style={{ fontSize: "1.6rem", fontWeight: 800, color: c }}>{v}</p>
              </div>
            ))}
          </div>
          <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
            {users.users.map((u, i) => (
              <div key={u.phone} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: i < users.users.length - 1 ? `1px solid ${G.border}` : "none" }}>
                <div>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 3 }}>
                    <span style={{ width: 8, height: 8, borderRadius: "50%", background: u.active ? G.green : G.t3, display: "inline-block", flexShrink: 0 }} />
                    <span style={{ fontSize: "0.85rem", color: G.t1, fontWeight: 500 }}>+{u.phone}</span>
                  </div>
                  <p style={{ fontSize: "0.72rem", color: G.t3, marginLeft: 16 }}>{u.email || "No email yet"} · Last active: {u.last_active ? new Date(u.last_active).toLocaleDateString() : "—"}</p>
                </div>
                <div style={{ display: "flex", gap: 12, textAlign: "right" }}>
                  <div><p style={{ fontSize: "0.68rem", color: G.t3 }}>Jobs</p><p style={{ fontWeight: 700, color: G.accent }}>{u.total_jobs}</p></div>
                  <div><p style={{ fontSize: "0.68rem", color: G.t3 }}>Applied</p><p style={{ fontWeight: 700, color: G.green }}>{u.applied}</p></div>
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Companies */}
      {tab === "companies" && (
        <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}` }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 14 }}>{companies.length} companies tracked</p>
          {companies.map((c, i) => (
            <div key={c.company} style={{ padding: "14px 0", borderBottom: i < companies.length - 1 ? `1px solid ${G.border}` : "none" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 6 }}>
                <p style={{ fontSize: "0.9rem", fontWeight: 600, color: G.t1 }}>{c.company || "Unknown"}</p>
                <div style={{ display: "flex", gap: 8, flexShrink: 0, marginLeft: 12 }}>
                  <span style={{ fontSize: "0.72rem", color: G.accent, background: G.accentSoft, border: `1px solid ${G.accentBorder}`, borderRadius: 20, padding: "2px 8px" }}>{c.count} jobs</span>
                  <span style={{ fontSize: "0.72rem", color: G.amber, background: G.amberSoft, border: `1px solid ${G.amberBorder}`, borderRadius: 20, padding: "2px 8px" }}>{c.unique_users} students</span>
                </div>
              </div>
              <div style={{ display: "flex", flexWrap: "wrap", gap: 5 }}>
                {c.roles.filter(Boolean).map(r => (
                  <span key={r} style={{ fontSize: "0.7rem", color: G.t2, background: G.b1, border: `1px solid ${G.border}`, borderRadius: 6, padding: "2px 8px" }}>{r}</span>
                ))}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Jobs */}
      {tab === "jobs" && (
        <div>
          <p style={{ fontSize: "0.68rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 14 }}>{jobs.length} total jobs</p>
          {jobs.map(j => (
            <div key={j._id} style={{ background: G.b2, borderRadius: 12, padding: "14px 16px", marginBottom: 8, border: `1px solid ${G.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ fontSize: "0.88rem", fontWeight: 600, color: G.t1 }}>{j.company_name || "Unknown"}</p>
                <p style={{ fontSize: "0.75rem", color: G.accent, marginTop: 2 }}>{j.role}</p>
                <p style={{ fontSize: "0.68rem", color: G.t3, marginTop: 4 }}>+{j.user_id} · {j.applied ? "✓ Applied" : "Pending"} · {j.created_at ? new Date(j.created_at).toLocaleDateString() : "—"}</p>
              </div>
              <button onClick={() => deleteJob(j._id)}
                style={{ background: G.redSoft, color: G.red, border: `1px solid ${G.red}40`, borderRadius: 8, padding: "6px 12px", fontSize: "0.78rem", cursor: "pointer", fontFamily: "inherit", flexShrink: 0, marginLeft: 12 }}>
                Delete
              </button>
            </div>
          ))}
        </div>
      )}

      {/* Broadcast */}
      {tab === "broadcast" && (
        <div style={{ background: G.b2, borderRadius: 16, padding: 24, border: `1px solid ${G.border}` }}>
          <p style={{ fontSize: "0.68rem", color: G.t3, letterSpacing: "0.12em", textTransform: "uppercase", marginBottom: 20 }}>Broadcast WhatsApp Message</p>

          <p style={{ fontSize: "0.78rem", color: G.t2, marginBottom: 8 }}>Target audience</p>
          <div style={{ display: "flex", gap: 8, marginBottom: 20 }}>
            {[["all", "All Users"], ["active", "Active (7d)"], ["inactive", "Inactive"]].map(([val, label]) => (
              <button key={val} onClick={() => setBroadcast(b => ({ ...b, target: val }))}
                style={{ padding: "7px 16px", borderRadius: 9, border: `1px solid ${broadcast.target === val ? G.accent : G.border}`, background: broadcast.target === val ? G.accentSoft : "transparent", color: broadcast.target === val ? G.accent : G.t2, cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit" }}>
                {label}
              </button>
            ))}
          </div>

          <p style={{ fontSize: "0.78rem", color: G.t2, marginBottom: 8 }}>Message <span style={{ color: G.t3 }}>({broadcast.message.length}/1000)</span></p>
          <textarea value={broadcast.message} onChange={e => setBroadcast(b => ({ ...b, message: e.target.value }))}
            placeholder="Type your message here..." rows={5}
            style={{ width: "100%", background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10, padding: "12px 14px", color: G.t1, fontSize: "0.9rem", fontFamily: "inherit", resize: "vertical", boxSizing: "border-box", marginBottom: 16 }} />

          <button onClick={sendBroadcast} disabled={broadcastLoading || !broadcast.message.trim()}
            style={{ background: broadcastLoading ? G.b3 : G.accent, color: "#fff", padding: "12px 24px", borderRadius: 10, border: "none", fontSize: "0.92rem", fontWeight: 600, cursor: broadcastLoading ? "not-allowed" : "pointer", fontFamily: "inherit", opacity: !broadcast.message.trim() ? 0.5 : 1 }}>
            {broadcastLoading ? "Sending…" : `Send to ${broadcast.target === "all" ? "all" : broadcast.target} users`}
          </button>

          {broadcastResult && (
            <div style={{ marginTop: 16, background: broadcastResult.error ? G.redSoft : G.greenSoft, border: `1px solid ${broadcastResult.error ? G.red : G.green}40`, borderRadius: 10, padding: "12px 16px" }}>
              {broadcastResult.error
                ? <p style={{ color: G.red, fontSize: "0.85rem" }}>Error: {broadcastResult.error}</p>
                : <p style={{ color: G.green, fontSize: "0.85rem" }}>✓ Sent to {broadcastResult.sent} users · {broadcastResult.failed} failed</p>
              }
            </div>
          )}
        </div>
      )}
    </div>
  );
}
