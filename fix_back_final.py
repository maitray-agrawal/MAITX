with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    lines = f.readlines()

back_btn = '      {onBack && (\n        <button onClick={onBack} style={{ background: "transparent", color: "#8888aa", border: "1px solid #25253a", borderRadius: 9, padding: "7px 14px", fontSize: "0.82rem", fontFamily: "inherit", cursor: "pointer", marginBottom: 20, display: "inline-flex", alignItems: "center", gap: 6 }}>\u2190 Back to Dashboard</button>\n      )}\n'

lines.insert(366, back_btn)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.writelines(lines)
print("Done")
