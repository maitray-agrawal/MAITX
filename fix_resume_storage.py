content = '''from pymongo import MongoClient
from gridfs import GridFS
from app.extractor_agent import JobRecord
from datetime import datetime
from bson import ObjectId
import os
import certifi

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["tnp_tracker"]
jobs_collection = db["jobs"]
resumes_collection = db["resumes"]
users_collection = db["users"]
fs = GridFS(db, collection="resume_files")

# OTP store
otp_collection = db["otp_store"]

def ensure_indexes():
    try:
        otp_collection.create_index("created_at", expireAfterSeconds=600)
        print("MongoDB indexes created")
    except Exception as e:
        print(f"Index creation warning: {e}")

async def save_job(job: JobRecord, user_id: str):
    from datetime import timedelta
    recent = jobs_collection.find_one({
        "user_id": user_id,
        "company_name": job.company_name,
        "role": job.role,
        "created_at": {"$gte": datetime.utcnow() - timedelta(minutes=5)}
    })
    if recent:
        print(f"Duplicate detected, skipping: {job.company_name} - {job.role}")
        return None
    doc = job.dict()
    doc["user_id"] = user_id
    doc["notified"] = False
    doc["created_at"] = datetime.utcnow()
    doc["ats_score"] = None
    doc["ats_analysis"] = None
    result = jobs_collection.insert_one(doc)
    return str(result.inserted_id)

async def get_recent_job_by_keyword(keyword: str, user_id: str):
    doc = jobs_collection.find_one(
        {
            "user_id": user_id,
            "company_name": {"$regex": keyword, "$options": "i"}
        },
        sort=[("created_at", -1)]
    )
    return doc

async def update_job(job_id: ObjectId, updated: JobRecord):
    updated_fields = {k: v for k, v in updated.dict().items() if v is not None}
    jobs_collection.update_one(
        {"_id": job_id},
        {"$set": updated_fields}
    )

async def get_jobs_near_deadline():
    cursor = jobs_collection.find({"notified": False})
    return list(cursor)

def save_resume_to_gridfs(pdf_bytes: bytes, filename: str, user_id: str) -> str:
    file_id = fs.put(pdf_bytes, filename=filename, user_id=user_id, uploaded_at=datetime.utcnow())
    return str(file_id)

def get_resume_from_gridfs(file_id: str) -> bytes:
    f = fs.get(ObjectId(file_id))
    return f.read()

def delete_resume_from_gridfs(file_id: str):
    fs.delete(ObjectId(file_id))
'''

with open("app/database.py", "w", encoding="utf-8") as f:
    f.write(content)
print("database.py updated with GridFS + resumes collection")