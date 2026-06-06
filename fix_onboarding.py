# Fix 1: Add users_collection to database.py
with open("app/database.py", encoding="utf-8") as f:
    content = f.read()

if "users_collection" not in content:
    content += "\nusers_collection = db[\"users\"]\n"
    with open("app/database.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("database.py updated")
else:
    print("users_collection already exists")