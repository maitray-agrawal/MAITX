import os
import random
import jwt
import httpx
from datetime import datetime, timedelta
from app.database import otp_collection

JWT_SECRET = os.getenv("JWT_SECRET", "maitx_super_secret_change_in_prod")
JWT_EXPIRY_HOURS = 24 * 7

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def create_jwt(user_id: str) -> str:
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXPIRY_HOURS)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm="HS256")

def verify_jwt(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

async def send_otp(phone: str) -> bool:
    otp = generate_otp()
    otp_collection.delete_many({"phone": phone})
    otp_collection.insert_one({
        "phone": phone,
        "otp": otp,
        "created_at": datetime.utcnow()
    })
    email = phone.strip()
    api_key = os.getenv("BREVO_API_KEY", "")
    sender_email = os.getenv("BREVO_SENDER", "")
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                "https://api.brevo.com/v3/smtp/email",
                headers={
                    "api-key": api_key,
                    "Content-Type": "application/json"
                },
                json={
                    "sender": {"name": "MAITX", "email": sender_email},
                    "to": [{"email": email}],
                    "subject": f"MAITX OTP: {otp}",
                    "textContent": f"Your MAITX verification code is: {otp}\n\nValid for 10 minutes. Do not share this with anyone.\n— MAITX TnP Tracker"
                }
            )
        print(f"Brevo response: {r.status_code} {r.text}")
        return r.status_code == 201
    except Exception as e:
        print(f"Email send error: {e}")
        return False

def verify_otp(phone: str, otp: str) -> bool:
    record = otp_collection.find_one({"phone": phone, "otp": otp})
    if record:
        otp_collection.delete_one({"_id": record["_id"]})
        return True
    return False
