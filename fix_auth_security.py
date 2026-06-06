with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

# Fix 1: validation message - email not phone
content = content.replace(
    'if (!val || val.length < 10) { setError("Enter a valid number with country code"); return; }',
    'if (!val || !val.includes("@")) { setError("Enter a valid email address"); return; }'
)

# Fix 2: OTP expired error message
content = content.replace(
    'setError(e.response?.data?.detail || "Invalid OTP. Try again.");',
    'const msg = e.response?.data?.detail || "Invalid OTP. Try again.";\n      setError(msg.includes("expired") ? "OTP expired. Please request a new one." : msg);'
)

# Fix 3: hint text cleanup
content = content.replace(
    'Enter emailto receive OTP · 91XXXXXXXXXX for India',
    'Enter your email address to receive OTP'
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)
print("App.js auth fixes applied")