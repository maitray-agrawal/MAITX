with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# 1. Add prefilledJob state to main App
content = content.replace(
    'const [userId, setUserId] = useState(getStoredUser() || "");',
    'const [userId, setUserId] = useState(getStoredUser() || "");\n  const [activeTab, setActiveTab] = useState("jobs");\n  const [prefilledJob, setPrefilledJob] = useState(null);'
)

# 2. Remove activeTab state from wherever it was declared inline (it may be duplicate)
# Check if there's a duplicate - replace only first occurrence if so
content = content.replace(
    '  const [activeTab, setActiveTab] = useState("jobs");\n  const [activeTab, setActiveTab] = useState("jobs");',
    '  const [activeTab, setActiveTab] = useState("jobs");'
)

# 3. Pass prefilledJob to ResumeTailor
content = content.replace(
    'if (activeTab === "resume") return <ResumeTailor token={getToken()} />;',
    'if (activeTab === "resume") return <ResumeTailor token={getToken()} prefilledJob={prefilledJob} onBack={() => { setActiveTab("jobs"); setPrefilledJob(null); }} />;'
)

# 4. Add onTailor prop to JobCard call
content = content.replace(
    ': filtered.map((job, i) => (\n            <JobCard key={job._id} job={job} index={i} onMarkApplied={markApplied} onDelete={deleteJob} />',
    ': filtered.map((job, i) => (\n            <JobCard key={job._id} job={job} index={i} onMarkApplied={markApplied} onDelete={deleteJob} onTailor={(job) => { setPrefilledJob(job); setActiveTab("resume"); }} />'
)

# 5. Add onTailor button to JobCard component
content = content.replace(
    'function JobCard({ job, onMarkApplied, onDelete, index }) {',
    'function JobCard({ job, onMarkApplied, onDelete, onTailor, index }) {'
)

content = content.replace(
    '{job.apply_link && (\n        <a href={job.apply_link} target="_blank" rel="noreferrer"',
    '''{onTailor && (
        <button className="btn" onClick={() => onTailor(job)} style={{ background: G.accentSoft, color: G.accent, padding: "6px 12px", borderRadius: 8, border: `1px solid ${G.accentBorder}`, fontSize: "0.78rem", fontFamily: "inherit" }}>✨ Tailor Resume</button>
      )}
      {job.apply_link && (
        <a href={job.apply_link} target="_blank" rel="noreferrer"'''
)

# 6. Update ResumeTailor to accept prefilledJob and auto-fill JD
content = content.replace(
    'function ResumeTailor({ token }) {',
    'function ResumeTailor({ token, prefilledJob, onBack }) {'
)

content = content.replace(
    '  const [jd, setJd] = useState("");',
    '''  const [jd, setJd] = useState("");
  const [autoAnalyzing, setAutoAnalyzing] = useState(false);'''
)

# Auto-fill JD when prefilledJob is provided
content = content.replace(
    '  useEffect(() => { fetchResumes(); }, []);',
    '''  useEffect(() => { fetchResumes(); }, []);

  useEffect(() => {
    if (prefilledJob) {
      const jdText = [
        prefilledJob.company_name,
        prefilledJob.role,
        prefilledJob.eligibility,
        prefilledJob.extra_notes,
        prefilledJob.work_format,
        prefilledJob.location
      ].filter(Boolean).join("\\n");
      setJd(jdText);
      setActiveTab("analyze");
    }
  }, [prefilledJob]);'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("App.js updated with Tailor from job card flow")