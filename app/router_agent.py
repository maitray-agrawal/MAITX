from groq import Groq
import os
import json
from app.extractor_agent import extract_job_details
from app.database import save_job, get_recent_job_by_keyword, update_job, jobs_collection
from app.whatsapp import send_message

DASHBOARD_URL = "https://maitx.vercel.app"  


def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def is_new_user(sender: str) -> bool:
    count = jobs_collection.count_documents({"user_id": sender})
    return count == 0


def classify_message(text: str) -> dict:
    prompt = f"""
Classify the following message into exactly one of these intents:
- NEW_JD : a new internship or job description with details like company, role, deadline
- UPDATE  : an update to a previously mentioned opportunity
- JUNK   : irrelevant message, chatter, forwards, greetings

Return ONLY a JSON object like:
{{"intent": "NEW_JD", "keyword": null}}
or
{{"intent": "UPDATE", "keyword": "Amazon"}}
or
{{"intent": "JUNK", "keyword": null}}

Message:
{text}
"""
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    raw = response.choices[0].message.content.strip()
    try:
        return json.loads(raw)
    except Exception as e:
        print(f"Router parsing error: {e}")
        return {"intent": "JUNK", "keyword": None}


async def classify_and_process(text: str, sender: str):
    print(f"Classifying message from {sender}...")

    # Welcome new users
    new_user = is_new_user(sender)

    try:
        result = classify_message(text)
    except Exception as e:
        print(f"Groq error: {e}")
        await send_message(
            sender,
            "MAITX is temporarily busy. Please try again in a few minutes."
        )
        return

    intent = result.get("intent", "JUNK")
    keyword = result.get("keyword")
    print(f"Intent: {intent} | Keyword: {keyword}")

    if intent == "JUNK":
        if new_user:
            await send_message(
                sender,
                "👋 Welcome to *MAITX*!\n\n"
                "I'm your AI-powered internship tracker.\n\n"
                "📌 *How to use:*\n"
                "Forward any TnP internship message to me and I'll automatically extract and save it for you.\n\n"
                f"📊 *Your Dashboard:*\n{DASHBOARD_URL}\n"
                f"Login with your number: *{sender}*\n\n"
                "Start by forwarding a TnP message! 🚀"
            )
        else:
            print("Junk message ignored")
        return

    elif intent == "NEW_JD":
        try:
            job = extract_job_details(text)
            if job:
                await save_job(job, sender)
                print(f"Saved: {job.company_name} - {job.role}")

                # Build confirmation message
                msg = f"✅ Saved *{job.company_name}* - *{job.role}*\n"
                if job.deadline: msg += f"📅 Deadline: {job.deadline}\n"
                if job.stipend: msg += f"💰 Stipend: {job.stipend}\n"
                if job.work_format: msg += f"🏢 Format: {job.work_format}\n"
                if job.apply_link: msg += f"🔗 Apply: {job.apply_link}\n"
                msg += f"\n📊 View dashboard: {DASHBOARD_URL}"

                # Add welcome note for first job saved
                if new_user:
                    msg += f"\n\n👋 Welcome to MAITX! Login with *{sender}*"

                await send_message(sender, msg)
            else:
                print("Extraction failed")
                await send_message(
                    sender,
                    "Sorry, could not extract job details. Please forward the full JD."
                )
        except Exception as e:
            print(f"Extraction error: {e}")
            await send_message(
                sender,
                "MAITX is temporarily busy. Please try again in a few minutes."
            )

    elif intent == "UPDATE":
        if keyword:
            existing = await get_recent_job_by_keyword(keyword, sender)
            if existing:
                updated = extract_job_details(text)
                if updated:
                    await update_job(existing["_id"], updated)
                    print(f"Updated record for {keyword}")
                    await send_message(sender, f"Updated the *{keyword}* opportunity!")
            else:
                print(f"No existing record found for: {keyword}")
                await send_message(sender, f"Could not find a saved record for *{keyword}*.")
