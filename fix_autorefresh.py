with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'useEffect(() => { if (userId) fetchJobs(); }, [userId, fetchJobs]);',
    '''useEffect(() => { if (userId) fetchJobs(); }, [userId, fetchJobs]);
  useEffect(() => {
    if (!userId) return;
    const interval = setInterval(fetchJobs, 30000);
    return () => clearInterval(interval);
  }, [userId, fetchJobs]);'''
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Auto-refresh added")