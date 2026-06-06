content = """import os
import random
import jwt
import httpx
from datetime import datetime, timedelta
from app.database import otp_collection

JWT_SECRET = os.getenv("JWT_SECRET", "maitx_super_secret_change_in_prod")
JWT_EXPIRY_HOURS = 24 * 7  # 7 days


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

    # Strip country code for Fast2SMS — it needs 10-digit Indian number
    number = phone[-10:]

    try:
        async with httpx.AsyncClient() as client:
            resp = await client.post(
                "https://www.fast2sms.com/dev/bulkV2",
                headers={"authorization": os.getenv("FAST2SMS_KEY", "")},
                json={
                    "route": "otp",
                    "variables_values": otp,
                    "numbers": number,
                }
            )
        result = resp.json()
        print(f"Fast2SMS response: {result}")
        return result.get("return") is True
    except Exception as e:
        print(f"SMS send error: {e}")
        return False


def verify_otp(phone: str, otp: str) -> bool:
    record = otp_collection.find_one({"phone": phone, "otp": otp})
    if record:
        otp_collection.delete_one({"_id": record["_id"]})
        return True
    return False
"""

with open("app/auth.py", "w", encoding="utf-8") as f:
    f.write(content)
print("app/auth.py updated — SMS OTP via Fast2SMS")