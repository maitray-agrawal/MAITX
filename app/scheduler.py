from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database import jobs_collection
from app.whatsapp import send_message
from datetime import datetime, timedelta
import re

scheduler = AsyncIOScheduler()


def parse_deadline(deadline_str: str):
    if not deadline_str:
        return None

    # Remove time part e.g. "till 4:00 PM", "till 5:00 pm"
    cleaned = re.sub(r"till\s+\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)", "", deadline_str, flags=re.IGNORECASE)
    cleaned = re.sub(r",?\s*\d{1,2}(:\d{2})?\s*(AM|PM|am|pm)", "", cleaned, flags=re.IGNORECASE)

    # Remove ordinal suffixes
    cleaned = re.sub(r"(\d+)(st|nd|rd|th)", r"", cleaned, flags=re.IGNORECASE)

    # Replace dots with spaces e.g. 31.5.2026
    cleaned = re.sub(r"(\d+)\.(\d+)\.(\d+)", r"  ", cleaned)

    cleaned = re.sub(r"\s+", " ", cleaned).strip()

    formats = [
        "%d %B %Y", "%d %b %Y", "%B %d %Y",
        "%d/%m/%Y", "%m/%d/%Y", "%Y-%m-%d",
        "%d-%m-%Y", "%d %B, %Y", "%d %b, %Y",
        "%d %m %Y", "%Y %m %d",
        "%d %B", "%d %b"
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(cleaned, fmt)
            if dt.year == 1900:
                dt = dt.replace(year=datetime.utcnow().year)
            return dt
        except ValueError:
            continue

    print(f"Could not parse deadline: {deadline_str}")
    return None


async def check_deadlines():
    print(f"Checking deadlines at {datetime.utcnow()}")
    now = datetime.utcnow()
    window = now + timedelta(hours=48)
    jobs = list(jobs_collection.find({"notified": False}))
    print(f"Found {len(jobs)} unnotified jobs")

    for job in jobs:
        deadline_str = job.get("deadline")
        if not deadline_str:
            print(f"No deadline for {job.get('company_name')}, skipping")
            continue

        deadline_dt = parse_deadline(deadline_str)
        if not deadline_dt:
            continue

        print(f"Parsed deadline for {job.get('company_name')}: {deadline_dt}")

        if now <= deadline_dt <= window:
            user_id = job.get("user_id")
            company = job.get("company_name", "Unknown")
            role = job.get("role", "Unknown")
            link = job.get("apply_link", "No link provided")

            message = (
                f"Deadline Alert! {company} - {role}\n"
                f"Deadline: {deadline_str}\n"
                f"Apply: {link}\n"
                f"Do not miss it!"
            )

            await send_message(user_id, message)
            jobs_collection.update_one(
                {"_id": job["_id"]},
                {"$set": {"notified": True}}
            )
            print(f"Reminder sent for {company} to {user_id}")
        else:
            print(f"Deadline not in window for {job.get('company_name')}: {deadline_dt}")


def start_scheduler():
    scheduler.add_job(check_deadlines, "interval", hours=6)
    scheduler.start()
    print("Scheduler started")
