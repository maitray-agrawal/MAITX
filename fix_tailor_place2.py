with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if '<TailorSection token={token} jobId={jobId} />' in line:
        lines.pop(i)
        # Insert after the </div> closing the tab content (line 265 becomes 264 after pop)
        lines.insert(i+1, '      <TailorSection token={token} jobId={jobId} />\n')
        break

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Fixed")