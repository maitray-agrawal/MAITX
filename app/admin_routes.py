from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import jobs_collection, otp_collection
from app.auth import verify_jwt, create_jwt
import os

router = APIRouter()
security = HTTPBearer()

ADMIN_SECRET = os.getenv("ADMIN_SECRET", "maitx_admin_change_this")

def get_admin_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload["user_id"]

@router.post("/admin/login")
async def admin_login(body: dict):
    secret = body.get("secret", "").strip()
    if secret != ADMIN_SECRET:
        raise HTTPException(status_code=401, detail="Invalid admin secret")
    import jwt
    from datetime import datetime, timedelta
    payload = {
        "user_id": "admin",
        "role": "admin",
        "exp": datetime.utcnow() + timedelta(hours=12)
    }
    token = jwt.encode(payload, os.getenv("JWT_SECRET", "maitx_super_secret_change_in_prod"), algorithm="HS256")
    return {"token": token}

@router.get("/admin/stats")
async def admin_stats(admin: str = Depends(get_admin_user)):
    total_jobs = jobs_collection.count_documents({})
    total_applied = jobs_collection.count_documents({"applied": True})
    total_users = len(jobs_collection.distinct("user_id"))
    active_otps = otp_collection.count_documents({})

    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "total": {"$sum": 1},
            "applied": {"$sum": {"$cond": ["$applied", 1, 0]}}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 20}
    ]
    users = list(jobs_collection.aggregate(pipeline))
    for u in users:
        u["user_id"] = u.pop("_id")

    return {
        "total_jobs": total_jobs,
        "total_applied": total_applied,
        "total_users": total_users,
        "active_otps": active_otps,
        "apply_rate": round((total_applied / total_jobs * 100), 1) if total_jobs > 0 else 0,
        "users": users
    }

@router.get("/admin/jobs")
async def admin_all_jobs(admin: str = Depends(get_admin_user), limit: int = 50):
    jobs = list(jobs_collection.find().sort("created_at", -1).limit(limit))
    for j in jobs:
        j["_id"] = str(j["_id"])
    return jobs

@router.delete("/admin/jobs/{job_id}")
async def admin_delete_job(job_id: str, admin: str = Depends(get_admin_user)):
    from bson import ObjectId
    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return {"status": "deleted"}

@router.get("/admin/users")
async def admin_users(admin: str = Depends(get_admin_user)):
    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "total_jobs": {"$sum": 1},
            "applied": {"$sum": {"$cond": ["$applied", 1, 0]}},
            "last_active": {"$max": "$created_at"}
        }},
        {"$sort": {"last_active": -1}}
    ]
    users = list(jobs_collection.aggregate(pipeline))
    for u in users:
        u["user_id"] = u.pop("_id")
        u["last_active"] = u["last_active"].isoformat() if u.get("last_active") else None
    return {"users": users, "total": len(users)}
