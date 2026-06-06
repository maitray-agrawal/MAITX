with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    lines = f.readlines()

# Insert TailorSection before the closing </div> of ResumeResults (line 266, index 265)
tailor_insert = '      <TailorSection token={token} jobId={jobId} />\n'
lines.insert(265, tailor_insert)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("TailorSection inserted into ResumeResults")