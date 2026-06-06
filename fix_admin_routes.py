content = '''from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.database import jobs_collection, otp_collection, users_collection
from app.auth import verify_jwt
from app.whatsapp import send_message
import os
import asyncio

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

    # Top companies
    company_pipeline = [
        {"$group": {"_id": "$company_name", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    top_companies = list(jobs_collection.aggregate(company_pipeline))
    for c in top_companies:
        c["company"] = c.pop("_id")

    # Per user stats
    user_pipeline = [
        {"$group": {
            "_id": "$user_id",
            "total": {"$sum": 1},
            "applied": {"$sum": {"$cond": ["$applied", 1, 0]}},
            "last_active": {"$max": "$created_at"}
        }},
        {"$sort": {"total": -1}},
        {"$limit": 20}
    ]
    users = list(jobs_collection.aggregate(user_pipeline))
    for u in users:
        u["user_id"] = u.pop("_id")

    return {
        "total_jobs": total_jobs,
        "total_applied": total_applied,
        "total_users": total_users,
        "active_otps": active_otps,
        "apply_rate": round((total_applied / total_jobs * 100), 1) if total_jobs > 0 else 0,
        "top_companies": top_companies,
        "users": users
    }

@router.get("/admin/jobs")
async def admin_all_jobs(admin: str = Depends(get_admin_user), limit: int = 50):
    jobs = list(jobs_collection.find().sort("created_at", -1).limit(limit))
    for j in jobs:
        j["_id"] = str(j["_id"])
        if j.get("created_at"):
            j["created_at"] = j["created_at"].isoformat()
    return jobs

@router.delete("/admin/jobs/{job_id}")
async def admin_delete_job(job_id: str, admin: str = Depends(get_admin_user)):
    from bson import ObjectId
    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return {"status": "deleted"}

@router.get("/admin/users")
async def admin_users(admin: str = Depends(get_admin_user)):
    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=7)

    pipeline = [
        {"$group": {
            "_id": "$user_id",
            "total_jobs": {"$sum": 1},
            "applied": {"$sum": {"$cond": ["$applied", 1, 0]}},
            "last_active": {"$max": "$created_at"}
        }},
        {"$sort": {"last_active": -1}}
    ]
    job_stats = {u["_id"]: u for u in jobs_collection.aggregate(pipeline)}

    # Merge with users collection for email
    all_users = list(users_collection.find())
    result = []
    for u in all_users:
        phone = u.get("phone")
        stats = job_stats.get(phone, {})
        last_active = stats.get("last_active")
        result.append({
            "phone": phone,
            "email": u.get("email"),
            "onboarding": u.get("onboarding", False),
            "total_jobs": stats.get("total_jobs", 0),
            "applied": stats.get("applied", 0),
            "last_active": last_active.isoformat() if last_active else None,
            "active": last_active > cutoff if last_active else False
        })

    result.sort(key=lambda x: x["last_active"] or "", reverse=True)
    active_count = sum(1 for u in result if u["active"])

    return {
        "users": result,
        "total": len(result),
        "active": active_count,
        "inactive": len(result) - active_count
    }

@router.get("/admin/companies")
async def admin_companies(admin: str = Depends(get_admin_user)):
    pipeline = [
        {"$group": {
            "_id": "$company_name",
            "count": {"$sum": 1},
            "roles": {"$addToSet": "$role"},
            "users": {"$addToSet": "$user_id"}
        }},
        {"$sort": {"count": -1}},
        {"$limit": 50}
    ]
    companies = list(jobs_collection.aggregate(pipeline))
    for c in companies:
        c["company"] = c.pop("_id")
        c["unique_users"] = len(c.pop("users"))
        c["roles"] = [r for r in c["roles"] if r][:5]  # top 5 roles
    return {"companies": companies, "total": len(companies)}

@router.post("/admin/broadcast")
async def admin_broadcast(body: dict, admin: str = Depends(get_admin_user)):
    message = body.get("message", "").strip()
    target = body.get("target", "all")  # "all" | "active" | "inactive"

    if not message:
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    if len(message) > 1000:
        raise HTTPException(status_code=400, detail="Message too long (max 1000 chars)")

    from datetime import datetime, timedelta
    cutoff = datetime.utcnow() - timedelta(days=7)

    # Get all onboarded users
    all_users = list(users_collection.find({"email": {"$ne": None}, "onboarding": False}))

    if target == "active":
        job_stats = {u["_id"]: u["last_active"] for u in jobs_collection.aggregate([
            {"$group": {"_id": "$user_id", "last_active": {"$max": "$created_at"}}}
        ])}
        recipients = [u for u in all_users if job_stats.get(u["phone"], datetime.min) > cutoff]
    elif target == "inactive":
        job_stats = {u["_id"]: u["last_active"] for u in jobs_collection.aggregate([
            {"$group": {"_id": "$user_id", "last_active": {"$max": "$created_at"}}}
        ])}
        recipients = [u for u in all_users if job_stats.get(u["phone"], datetime.min) <= cutoff]
    else:
        recipients = all_users

    if not recipients:
        return {"status": "no_recipients", "sent": 0}

    # Send with small delay to avoid Meta rate limits
    sent = 0
    failed = 0
    for user in recipients:
        try:
            await send_message(user["phone"], message)
            sent += 1
            await asyncio.sleep(0.3)  # 3 messages/second max
        except Exception as e:
            print(f"Broadcast failed for {user['phone']}: {e}")
            failed += 1

    return {
        "status": "done",
        "sent": sent,
        "failed": failed,
        "total_recipients": len(recipients),
        "target": target
    }
'''

with open("app/admin_routes.py", "w", encoding="utf-8") as f:
    f.write(content)
print("app/admin_routes.py updated")