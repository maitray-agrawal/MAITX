with open("app/auth_routes.py", encoding="utf-8") as f:
    content = f.read()

# Add rate limit decorator to request-otp endpoint
content = content.replace(
    'from fastapi import APIRouter, HTTPException, Depends\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\nfrom pydantic import BaseModel\nfrom app.auth import send_otp, verify_otp, create_jwt, verify_jwt\nfrom app.database import users_collection',
    'from fastapi import APIRouter, HTTPException, Depends, Request\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\nfrom pydantic import BaseModel\nfrom app.auth import send_otp, verify_otp, create_jwt, verify_jwt\nfrom app.database import users_collection\nfrom slowapi import Limiter\nfrom slowapi.util import get_remote_address\nlimiter = Limiter(key_func=get_remote_address)'
)

content = content.replace(
    '@router.post("/auth/request-otp")\nasync def request_otp(body: OTPRequest):',
    '@router.post("/auth/request-otp")\n@limiter.limit("5/minute")\nasync def request_otp(request: Request, body: OTPRequest):'
)

content = content.replace(
    '@router.post("/auth/verify-otp")\nasync def verify_otp_route(body: OTPVerify):',
    '@router.post("/auth/verify-otp")\n@limiter.limit("10/minute")\nasync def verify_otp_route(request: Request, body: OTPVerify):'
)

with open("app/auth_routes.py", "w", encoding="utf-8") as f:
    f.write(content)
print("auth_routes.py rate limiting applied")
