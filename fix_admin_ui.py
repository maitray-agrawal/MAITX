content = '''import React, { useState, useEffect } from "react";
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
  const [tab, setTab] = useState("stats");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const authH = () => ({ headers: { Authorization: `Bearer ${token}` } });

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

  const fetchStats = async () => {
    try {
      const r = await axios.get(`${API_BASE}/admin/stats`, authH());
      setStats(r.data);
    } catch { logout(); }
  };

  const fetchUsers = async () => {
    try {
      const r = await axios.get(`${API_BASE}/admin/users`, authH());
      setUsers(r.data.users);
    } catch (e) { console.error(e); }
  };

  const fetchJobs = async () => {
    try {
      const r = await axios.get(`${API_BASE}/admin/jobs`, authH());
      setJobs(r.data);
    } catch (e) { console.error(e); }
  };

  const deleteJob = async (id) => {
    await axios.delete(`${API_BASE}/admin/jobs/${id}`, authH());
    setJobs(jobs.filter(j => j._id !== id));
  };

  const logout = () => {
    localStorage.removeItem("maitx_admin_token");
    setToken(""); setStats(null); setUsers([]); setJobs([]);
  };

  useEffect(() => {
    if (!token) return;
    fetchStats();
    fetchUsers();
    fetchJobs();
  }, [token]);

  const card = (children, extra = {}) => (
    <div style={{ background: G.b2, borderRadius: 16, padding: 20, border: `1px solid ${G.border}`, ...extra }}>
      {children}
    </div>
  );

  const label = (text) => (
    <p style={{ fontSize: "0.68rem", letterSpacing: "0.12em", textTransform: "uppercase", color: G.t3, marginBottom: 8 }}>{text}</p>
  );

  if (!token) return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: G.bg, padding: 24 }}>
      <div style={{ width: "100%", maxWidth: 380 }}>
        <div style={{ textAlign: "center", marginBottom: 32 }}>
          <p style={{ fontSize: "0.68rem", letterSpacing: "0.2em", color: G.red, textTransform: "uppercase", marginBottom: 8 }}>Admin Access</p>
          <h1 style={{ fontSize: "2.5rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>MAITX</h1>
        </div>
        {card(<>
          {label("Admin Secret")}
          <input
            type="password" placeholder="Enter admin secret" value={secret}
            onChange={e => setSecret(e.target.value)}
            onKeyDown={e => e.key === "Enter" && login()}
            style={{ width: "100%", background: G.b1, border: `1px solid ${G.border}`, borderRadius: 10, padding: "12px 14px", color: G.t1, fontSize: "0.95rem", fontFamily: "inherit", marginBottom: 12, boxSizing: "border-box" }}
          />
          <button onClick={login} disabled={loading}
            style={{ width: "100%", background: G.red, color: "#fff", padding: 12, borderRadius: 10, border: "none", fontSize: "0.92rem", fontWeight: 600, cursor: "pointer", fontFamily: "inherit" }}>
            {loading ? "Verifying…" : "Login as Admin"}
          </button>
          {error && <p style={{ color: G.red, fontSize: "0.8rem", marginTop: 10, textAlign: "center" }}>{error}</p>}
        </>)}
      </div>
    </div>
  );

  return (
    <div style={{ minHeight: "100vh", background: G.bg, padding: "24px 16px 48px", maxWidth: 900, margin: "0 auto" }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 28 }}>
        <div>
          <p style={{ fontSize: "0.65rem", letterSpacing: "0.18em", color: G.red, textTransform: "uppercase", marginBottom: 4 }}>Admin Panel</p>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: G.t1 }}>MAITX</h1>
        </div>
        <button onClick={logout}
          style={{ background: "transparent", color: G.t3, padding: "7px 14px", borderRadius: 9, border: `1px solid ${G.border}`, fontSize: "0.8rem", cursor: "pointer", fontFamily: "inherit" }}>
          Logout
        </button>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 8, marginBottom: 24 }}>
        {["stats", "users", "jobs"].map(t => (
          <button key={t} onClick={() => setTab(t)}
            style={{ padding: "7px 18px", borderRadius: 9, border: `1px solid ${tab === t ? G.accent : G.border}`, background: tab === t ? G.accentSoft : "transparent", color: tab === t ? G.accent : G.t2, cursor: "pointer", fontSize: "0.82rem", fontFamily: "inherit", fontWeight: tab === t ? 600 : 400 }}>
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {/* Stats tab */}
      {tab === "stats" && stats && (
        <>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10, marginBottom: 10 }}>
            {[
              ["Total Jobs", stats.total_jobs, G.accent],
              ["Total Users", stats.total_users, G.amber],
              ["Apply Rate", `${stats.apply_rate}%`, G.green],
            ].map(([l, v, c]) => card(
              <><p style={{ fontSize: "0.68rem", color: G.t3, textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: 8 }}>{l}</p>
              <p style={{ fontSize: "2.2rem", fontWeight: 800, fontFamily: "'Syne',sans-serif", color: c }}>{v}</p></>,
              { key: l }
            ))}
          </div>
          <div style={{ marginTop: 10 }}>
            {card(<>
              {label("Top Users by Jobs Saved")}
              {stats.users.map((u, i) => (
                <div key={u.user_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "10px 0", borderBottom: i < stats.users.length - 1 ? `1px solid ${G.border}` : "none" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{ fontSize: "0.72rem", color: G.t3, width: 20 }}>#{i + 1}</span>
                    <span style={{ fontSize: "0.85rem", color: G.t1 }}>+{u.user_id}</span>
                  </div>
                  <div style={{ display: "flex", gap: 12 }}>
                    <span style={{ fontSize: "0.78rem", color: G.accent }}>{u.total} jobs</span>
                    <span style={{ fontSize: "0.78rem", color: G.green }}>{u.applied} applied</span>
                  </div>
                </div>
              ))}
            </>)}
          </div>
        </>
      )}

      {/* Users tab */}
      {tab === "users" && (
        card(<>
          {label(`${users.length} registered users`)}
          {users.map((u, i) => (
            <div key={u.user_id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "12px 0", borderBottom: i < users.length - 1 ? `1px solid ${G.border}` : "none" }}>
              <div>
                <p style={{ fontSize: "0.88rem", color: G.t1, fontWeight: 500 }}>+{u.user_id}</p>
                <p style={{ fontSize: "0.72rem", color: G.t3, marginTop: 2 }}>Last active: {u.last_active ? new Date(u.last_active).toLocaleDateString() : "—"}</p>
              </div>
              <div style={{ display: "flex", gap: 10, textAlign: "right" }}>
                <div><p style={{ fontSize: "0.75rem", color: G.t3 }}>Jobs</p><p style={{ fontSize: "1rem", fontWeight: 700, color: G.accent }}>{u.total_jobs}</p></div>
                <div><p style={{ fontSize: "0.75rem", color: G.t3 }}>Applied</p><p style={{ fontSize: "1rem", fontWeight: 700, color: G.green }}>{u.applied}</p></div>
              </div>
            </div>
          ))}
        </>)
      )}

      {/* Jobs tab */}
      {tab === "jobs" && (
        <div>
          {label(`${jobs.length} total jobs`)}
          {jobs.map((j, i) => (
            <div key={j._id} style={{ background: G.b2, borderRadius: 12, padding: "14px 16px", marginBottom: 8, border: `1px solid ${G.border}`, display: "flex", justifyContent: "space-between", alignItems: "center" }}>
              <div>
                <p style={{ fontSize: "0.88rem", fontWeight: 600, color: G.t1 }}>{j.company_name}</p>
                <p style={{ fontSize: "0.75rem", color: G.accent, marginTop: 2 }}>{j.role}</p>
                <p style={{ fontSize: "0.68rem", color: G.t3, marginTop: 4 }}>+{j.user_id} · {j.applied ? "✓ Applied" : "Pending"}</p>
              </div>
              <button onClick={() => deleteJob(j._id)}
                style={{ background: G.redSoft, color: G.red, border: `1px solid ${G.red}40`, borderRadius: 8, padding: "6px 12px", fontSize: "0.78rem", cursor: "pointer", fontFamily: "inherit" }}>
                Delete
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
'''

with open("maitx-dashboard/src/AdminPanel.jsx", "w", encoding="utf-8") as f:
    f.write(content)
print("AdminPanel.jsx created")