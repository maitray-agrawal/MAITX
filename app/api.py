from fastapi import APIRouter, Depends
from app.database import jobs_collection, users_collection
from app.auth_routes import get_current_user
from bson import ObjectId

router = APIRouter()

def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc

def resolve_phone(email: str) -> str:
    """Look up phone number from email in users collection."""
    user = users_collection.find_one({"email": email})
    if user:
        return user["phone"]
    # fallback: maybe email was used directly as user_id (old data)
    return email

@router.get("/api/jobs/{user_id}")
async def get_jobs(user_id: str, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    phone = resolve_phone(user_id)
    jobs = list(jobs_collection.find({"user_id": phone}).sort("created_at", -1))
    return [serialize(j) for j in jobs]

@router.get("/api/jobs/{user_id}/upcoming")
async def get_upcoming_jobs(user_id: str, current_user: str = Depends(get_current_user)):
    if current_user != user_id:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="Access denied")
    phone = resolve_phone(user_id)
    jobs = list(jobs_collection.find({
        "user_id": phone,
        "notified": False
    }).sort("created_at", -1))
    return [serialize(j) for j in jobs]

@router.patch("/api/jobs/{job_id}/applied")
async def mark_applied(job_id: str, current_user: str = Depends(get_current_user)):
    jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"applied": True}}
    )
    return {"status": "updated"}

@router.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, current_user: str = Depends(get_current_user)):
    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return {"status": "deleted"}
