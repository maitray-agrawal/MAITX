import os
import random
import jwt
from datetime import datetime, timedelta
from app.database import otp_collection
from app.whatsapp import send_message

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
    otp_collection.delete_many({"phone": phone})  # clear old OTPs
    otp_collection.insert_one({
        "phone": phone,
        "otp": otp,
        "created_at": datetime.utcnow()
    })
    try:
        await send_message(
            phone,
            f"🔐 *MAITX Verification*\n\n"
            f"Your OTP is: *{otp}*\n\n"
            f"Valid for 10 minutes. Do not share with anyone."
        )
        print(f"OTP sent to {phone}")
        return True
    except Exception as e:
        print(f"OTP send error: {e}")
        return False


def verify_otp(phone: str, otp: str) -> bool:
    record = otp_collection.find_one({"phone": phone, "otp": otp})
    if record:
        otp_collection.delete_one({"_id": record["_id"]})
        return True
    return False
