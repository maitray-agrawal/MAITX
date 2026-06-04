from pymongo import MongoClient
from app.extractor_agent import JobRecord
from datetime import datetime
from bson import ObjectId
import os
import certifi

MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client["tnp_tracker"]
jobs_collection = db["jobs"]


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

# OTP store — auto-expires after 10 minutes
otp_collection = db["otp_store"]
otp_collection.create_index("created_at", expireAfterSeconds=600)
