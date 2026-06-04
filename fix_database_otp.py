
content = """from pymongo import MongoClient
import os

client = MongoClient(os.getenv("MONGODB_URL"))
db = client["tnp_tracker"]

jobs_collection = db["jobs"]
otp_collection = db["otp_store"]

# Create TTL index — OTP auto-deletes after 10 minutes
otp_collection.create_index("created_at", expireAfterSeconds=600)

def get_collections():
    return jobs_collection, otp_collection
"""

with open("app/database.py", "r", encoding="utf-8") as f:
    existing = f.read()

# Only add otp_collection if not already present
if "otp_collection" not in existing:
    with open("app/database.py", "a", encoding="utf-8") as f:
        f.write("""
# OTP store — auto-expires after 10 minutes
otp_collection = db["otp_store"]
otp_collection.create_index("created_at", expireAfterSeconds=600)
""")
    print("otp_collection added to database.py")
else:
    print("otp_collection already exists, skipping")