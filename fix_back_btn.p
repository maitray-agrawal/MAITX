with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'if (activeTab === "resume") return <ResumeTailor token={getToken()} prefilledJob={prefilledJob} onBack={() => { setActiveTab("jobs"); setPrefilledJob(null); }} />;',
    '''if (activeTab === "resume") return (
    <div>
      <div style={{ maxWidth: 820, margin: "0 auto", padding: "24px 16px 0" }}>
        <button onClick={() => { setActiveTab("jobs"); setPrefilledJob(null); }}
          style={{ background: "transparent", color: "#8888aa", border: "1px solid #25253a", borderRadius: 9, padding: "7px 14px", fontSize: "0.82rem", fontFamily: "inherit", cursor: "pointer", marginBottom: 8 }}>
          ← Back to Dashboard
        </button>
      </div>
      <ResumeTailor token={getToken()} prefilledJob={prefilledJob} onBack={() => { setActiveTab("jobs"); setPrefilledJob(null); }} />
    </div>
  );'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Back button added")