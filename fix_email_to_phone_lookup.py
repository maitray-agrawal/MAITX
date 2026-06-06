# Fix auth_routes.py - validate email format instead of phone length
auth_routes = '''from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.auth import send_otp, verify_otp, create_jwt, verify_jwt
from app.database import users_collection

router = APIRouter()
security = HTTPBearer()

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

@router.post("/auth/request-otp")
async def request_otp(body: OTPRequest):
    email = body.phone.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    success = await send_otp(email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent via WhatsApp"}

@router.post("/auth/verify-otp")
async def verify_otp_route(body: OTPVerify):
    email = body.phone.strip().lower()
    otp = body.otp.strip()
    if verify_otp(email, otp):
        token = create_jwt(email)
        return {"token": token, "user_id": email}
    raise HTTPException(status_code=401, detail="Invalid or expired OTP")

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["user_id"]

@router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    # user_id is email — resolve phone from users collection
    user = users_collection.find_one({"email": user_id})
    phone = user["phone"] if user else None
    return {"user_id": user_id, "phone": phone}
'''

# Fix api.py - resolve email -> phone -> jobs
api = '''from fastapi import APIRouter, Depends
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
'''

with open("app/auth_routes.py", "w", encoding="utf-8") as f:
    f.write(auth_routes)
print("auth_routes.py updated")

with open("app/api.py", "w", encoding="utf-8") as f:
    f.write(api)
print("api.py updated")