content = open("app/database.py", encoding="utf-8").read()

marker = 'otp_collection = db["otp_store"]'
assert marker in content, "Marker not found"

addition = marker + chr(10) + chr(10) + "# Knowledge Vault" + chr(10) + 'knowledge_vault = db["knowledge_vault"]' + chr(10) + 'upload_logs = db["upload_logs"]'

content = content.replace(marker, addition, 1)

with open("app/database.py", "w", encoding="utf-8") as f:
    f.write(content)

print("Added knowledge_vault and upload_logs collections")