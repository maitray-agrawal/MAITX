with open("maitx-dashboard/src/App.js", encoding="utf-8") as f:
    content = f.read()

content = content.replace(
    'type="tel" placeholder="91XXXXXXXXXX" value={phone}',
    'type="email" placeholder="you@gmail.com" value={phone}'
)
content = content.replace(
    'Send OTP via WhatsApp',
    'Send OTP via Email'
)
content = content.replace(
    'Include country code',
    'Enter email to receive OTP'
)
content = content.replace(
    '📱 Check your SMS messages for the 6-digit code',
    '📧 Check your email inbox for the 6-digit code'
)

with open("maitx-dashboard/src/App.js", "w", encoding="utf-8") as f:
    f.write(content)

print("App.js updated for email login")