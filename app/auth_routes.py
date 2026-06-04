content = """from fastapi import APIRouter, HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from slowapi import Limiter
from slowapi.util import get_remote_address
from pydantic import BaseModel
from app.auth import send_otp, verify_otp, create_jwt, verify_jwt

limiter = Limiter(key_func=get_remote_address)
router = APIRouter()
security = HTTPBearer()


class OTPRequest(BaseModel):
    phone: str


class OTPVerify(BaseModel):
    phone: str
    otp: str


@router.post("/auth/request-otp")
@limiter.limit("3/minute")
async def request_otp(request: Request, body: OTPRequest):
    phone = body.phone.strip()
    if not phone or len(phone) < 10:
        raise HTTPException(status_code=400, detail="Invalid phone number")
    success = await send_otp(phone)
    if not success:
        raise HTTPException(status_code=500, detail="Failed to send OTP")
    return {"message": "OTP sent via WhatsApp"}


@router.post("/auth/verify-otp")
@limiter.limit("5/minute")
async def verify_otp_route(request: Request, body: OTPVerify):
    phone = body.phone.strip()
    otp = body.otp.strip()
    if verify_otp(phone, otp):
        token = create_jwt(phone)
        return {"token": token, "user_id": phone}
    raise HTTPException(status_code=401, detail="Invalid or expired OTP")


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    payload = verify_jwt(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return payload["user_id"]


@router.get("/auth/me")
async def get_me(user_id: str = Depends(get_current_user)):
    return {"user_id": user_id}
"""

with open("app/auth_routes.py", "w", encoding="utf-8") as f:
    f.write(content)
print("auth_routes.py updated with rate limiting")