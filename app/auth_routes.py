from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.auth import send_otp, verify_otp, create_jwt, verify_jwt
from app.database import users_collection
from slowapi import Limiter
from slowapi.util import get_remote_address
limiter = Limiter(key_func=get_remote_address)

router = APIRouter()
security = HTTPBearer()

class OTPRequest(BaseModel):
    phone: str

class OTPVerify(BaseModel):
    phone: str
    otp: str

@router.post("/auth/request-otp")
@limiter.limit("5/minute")
async def request_otp(request: Request, body: OTPRequest):
    email = body.phone.strip().lower()
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email address")
    success = await send_otp(email)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent via WhatsApp"}

@router.post("/auth/verify-otp")
@limiter.limit("10/minute")
async def verify_otp_route(request: Request, body: OTPVerify):
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
