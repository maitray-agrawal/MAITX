import os
import random
import jwt
import smtplib
from email.mime.text import MIMEText
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

    # phone field stores email when using email OTP
    email = phone.strip()
    gmail_user = os.getenv("GMAIL_USER", "")
    gmail_pass = os.getenv("GMAIL_PASS", "")

    try:
        msg = MIMEText(f"""
Hi,

Your MAITX verification code is:

{otp}

Valid for 10 minutes. Do not share this with anyone.

— MAITX TnP Tracker
""")
        msg["Subject"] = f"MAITX OTP: {otp}"
        msg["From"] = gmail_user
        msg["To"] = email

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(gmail_user, gmail_pass)
            server.sendmail(gmail_user, email, msg.as_string())

        print(f"OTP email sent to {email}")
        return True
    except Exception as e:
        print(f"Email send error: {e}")
        return False


def verify_otp(phone: str, otp: str) -> bool:
    record = otp_collection.find_one({"phone": phone, "otp": otp})
    if record:
        otp_collection.delete_one({"_id": record["_id"]})
        return True
    return False
