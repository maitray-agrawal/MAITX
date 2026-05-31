import { useState, useEffect, useCallback } from "react";
import axios from "axios";

const API_BASE = "https://web-production-c1e12.up.railway.app";

function App() {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("all");
  const [userId, setUserId] = useState(
    localStorage.getItem("maitx_user") || ""
  );
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
    if (val) {
      localStorage.setItem("maitx_user", val);
      setUserId(val);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem("maitx_user");
    setUserId("");
    setJobs([]);
    setLoading(true);
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
    if (filter === "applied") return j.applied;
    if (filter === "pending") return !j.applied;
    return true;
  });

  if (!userId) {
    return (
      <div style={styles.container}>
        <div style={styles.header}>
          <h1 style={styles.title}>MAITX</h1>
          <p style={styles.subtitle}>TnP Internship Tracker</p>
        </div>
        <div style={styles.loginBox}>
          <p style={{color: "#888", marginBottom: "16px", fontSize: "0.9rem"}}>
            Enter your WhatsApp number to view your saved jobs
          </p>
          <input
            type="tel"
            placeholder="91XXXXXXXXXX (with country code)"
            value={inputNumber}
            onChange={(e) => setInputNumber(e.target.value)}
            onKeyDown={(e) => { if (e.key === "Enter") handleLogin(); }}
            style={styles.input}
          />
          <button onClick={handleLogin} style={styles.loginBtn}>
            View My Jobs
          </button>
          <p style={{color: "#555", fontSize: "0.75rem", marginTop: "16px"}}>
            Forward TnP messages to MAITX WhatsApp bot to save jobs
          </p>
        </div>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>MAITX</h1>
        <p style={styles.subtitle}>TnP Internship Tracker</p>
        <button onClick={handleLogout} style={styles.logoutBtn}>
          Logout
        </button>
      </div>

      <div style={styles.statsRow}>
        <div style={styles.statCard}>
          <h2 style={styles.statNum}>{jobs.length}</h2>
          <p style={styles.statLabel}>Total</p>
        </div>
        <div style={styles.statCard}>
          <h2 style={styles.statNum}>{jobs.filter(j => !j.applied).length}</h2>
          <p style={styles.statLabel}>Pending</p>
        </div>
        <div style={styles.statCard}>
          <h2 style={styles.statNum}>{jobs.filter(j => j.applied).length}</h2>
          <p style={styles.statLabel}>Applied</p>
        </div>
      </div>

      <div style={styles.filterRow}>
        {["all", "pending", "applied"].map(f => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            style={{
              ...styles.filterBtn,
              background: filter === f ? "#6366f1" : "#1e1e2e",
              color: filter === f ? "#fff" : "#888"
            }}
          >
            {f.charAt(0).toUpperCase() + f.slice(1)}
          </button>
        ))}
        <button onClick={fetchJobs} style={styles.refreshBtn}>
          Refresh
        </button>
      </div>

      {loading ? (
        <p style={styles.center}>Loading...</p>
      ) : filtered.length === 0 ? (
        <p style={styles.center}>No jobs found</p>
      ) : (
        filtered.map(job => (
          <div key={job._id} style={{
            ...styles.card,
            borderLeft: job.applied ? "4px solid #22c55e" : "4px solid #6366f1"
          }}>
            <div style={styles.cardHeader}>
              <div>
                <h3 style={styles.company}>{job.company_name}</h3>
                <p style={styles.role}>{job.role}</p>
              </div>
              <span style={{
                ...styles.badge,
                background: job.applied ? "#22c55e22" : "#6366f122",
                color: job.applied ? "#22c55e" : "#6366f1"
              }}>
                {job.applied ? "Applied" : "Pending"}
              </span>
            </div>

            <div style={styles.details}>
              {job.deadline && <span style={styles.detail}>📅 {job.deadline}</span>}
              {job.stipend && <span style={styles.detail}>💰 {job.stipend}</span>}
              {job.work_format && <span style={styles.detail}>🏢 {job.work_format}</span>}
              {job.location && <span style={styles.detail}>📍 {job.location}</span>}
            </div>

            {job.eligibility && (
              <p style={styles.eligibility}>🎓 {job.eligibility}</p>
            )}

            {job.extra_notes && (
              <p style={styles.notes}>📝 {job.extra_notes}</p>
            )}

            <div style={styles.actions}>
              {job.apply_link && (
                <a href={job.apply_link} target="_blank" rel="noreferrer" style={styles.applyBtn}>
                  Apply Now
                </a>
              )}
              {!job.applied && (
                <button onClick={() => markApplied(job._id)} style={styles.doneBtn}>
                  Mark Applied
                </button>
              )}
              <button onClick={() => deleteJob(job._id)} style={styles.deleteBtn}>
                Delete
              </button>
            </div>
          </div>
        ))
      )}
    </div>
  );
}

const styles = {
  container: {
    minHeight: "100vh",
    background: "#0f0f1a",
    padding: "24px 16px",
    fontFamily: "'Segoe UI', sans-serif",
    maxWidth: "800px",
    margin: "0 auto"
  },
  header: {
    textAlign: "center",
    marginBottom: "32px"
  },
  title: {
    fontSize: "2.5rem",
    fontWeight: "800",
    color: "#6366f1",
    margin: 0
  },
  subtitle: {
    color: "#888",
    margin: "4px 0 8px"
  },
  logoutBtn: {
    background: "transparent",
    color: "#888",
    border: "1px solid #333",
    borderRadius: "6px",
    padding: "4px 12px",
    cursor: "pointer",
    fontSize: "0.75rem"
  },
  loginBox: {
    background: "#1e1e2e",
    borderRadius: "12px",
    padding: "32px",
    textAlign: "center",
    maxWidth: "400px",
    margin: "0 auto"
  },
  input: {
    background: "#2a2a3e",
    border: "1px solid #6366f1",
    borderRadius: "8px",
    padding: "12px 16px",
    color: "#fff",
    fontSize: "1rem",
    width: "100%",
    outline: "none",
    marginBottom: "12px",
    boxSizing: "border-box"
  },
  loginBtn: {
    background: "#6366f1",
    color: "#fff",
    padding: "12px 24px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontWeight: "600",
    fontSize: "1rem",
    width: "100%"
  },
  statsRow: {
    display: "flex",
    gap: "16px",
    marginBottom: "24px"
  },
  statCard: {
    flex: 1,
    background: "#1e1e2e",
    borderRadius: "12px",
    padding: "16px",
    textAlign: "center"
  },
  statNum: {
    color: "#6366f1",
    margin: 0,
    fontSize: "2rem"
  },
  statLabel: {
    color: "#888",
    margin: "4px 0 0",
    fontSize: "0.85rem"
  },
  filterRow: {
    display: "flex",
    gap: "8px",
    marginBottom: "24px",
    flexWrap: "wrap"
  },
  filterBtn: {
    padding: "8px 20px",
    borderRadius: "8px",
    border: "none",
    cursor: "pointer",
    fontWeight: "600"
  },
  refreshBtn: {
    padding: "8px 20px",
    borderRadius: "8px",
    border: "1px solid #333",
    background: "transparent",
    color: "#888",
    cursor: "pointer",
    fontWeight: "600",
    marginLeft: "auto"
  },
  card: {
    background: "#1e1e2e",
    borderRadius: "12px",
    padding: "20px",
    marginBottom: "16px"
  },
  cardHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "flex-start",
    marginBottom: "12px"
  },
  company: {
    color: "#fff",
    margin: 0,
    fontSize: "1.1rem"
  },
  role: {
    color: "#6366f1",
    margin: "4px 0 0",
    fontSize: "0.9rem"
  },
  badge: {
    padding: "4px 12px",
    borderRadius: "20px",
    fontSize: "0.75rem",
    fontWeight: "600",
    whiteSpace: "nowrap"
  },
  details: {
    display: "flex",
    flexWrap: "wrap",
    gap: "8px",
    marginBottom: "8px"
  },
  detail: {
    background: "#2a2a3e",
    color: "#ccc",
    padding: "4px 10px",
    borderRadius: "6px",
    fontSize: "0.8rem"
  },
  eligibility: {
    color: "#888",
    fontSize: "0.8rem",
    margin: "8px 0 4px"
  },
  notes: {
    color: "#666",
    fontSize: "0.8rem",
    margin: "4px 0"
  },
  actions: {
    display: "flex",
    gap: "8px",
    marginTop: "16px",
    flexWrap: "wrap"
  },
  applyBtn: {
    background: "#6366f1",
    color: "#fff",
    padding: "8px 16px",
    borderRadius: "8px",
    textDecoration: "none",
    fontSize: "0.85rem",
    fontWeight: "600"
  },
  doneBtn: {
    background: "#22c55e22",
    color: "#22c55e",
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #22c55e44",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: "600"
  },
  deleteBtn: {
    background: "#ef444422",
    color: "#ef4444",
    padding: "8px 16px",
    borderRadius: "8px",
    border: "1px solid #ef444444",
    cursor: "pointer",
    fontSize: "0.85rem",
    fontWeight: "600"
  },
  center: {
    color: "#888",
    textAlign: "center",
    marginTop: "40px"
  }
};

export default App;