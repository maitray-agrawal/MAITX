with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    lines = f.readlines()

# Find and fix - move TailorSection inside the closing div
for i, line in enumerate(lines):
    if '<TailorSection token={token} jobId={jobId} />' in line:
        tailor_line = lines.pop(i)
        # Insert it before the </div> closing tag (2 lines earlier now)
        lines.insert(i-1, tailor_line)
        break

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Fixed TailorSection placement")