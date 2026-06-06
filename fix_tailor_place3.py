with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Remove existing TailorSection line
content = content.replace('      <TailorSection token={token} jobId={jobId} />\n', '')

# Insert it after the closing )} of the tab section, before </div>
content = content.replace(
    '        </div>\n      )}\n    </div>\n  );\n}\n\nfunction ResumeTailor',
    '        </div>\n      )}\n      <TailorSection token={token} jobId={jobId} />\n    </div>\n  );\n}\n\nfunction ResumeTailor'
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("Fixed")