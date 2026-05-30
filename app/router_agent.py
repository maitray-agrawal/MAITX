from google import genai
import os
import json
from app.extractor_agent import extract_job_details
from app.database import save_job, get_recent_job_by_keyword, update_job
from app.whatsapp import send_message

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


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
    response = get_client().models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    raw = response.text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    try:
        return json.loads(raw.strip())
    except Exception as e:
        print(f"Router parsing error: {e}")
        return {"intent": "JUNK", "keyword": None}


async def classify_and_process(text: str, sender: str):
    print(f"Classifying message from {sender}...")
    result = classify_message(text)
    intent = result.get("intent", "JUNK")
    keyword = result.get("keyword")
    print(f"Intent: {intent} | Keyword: {keyword}")
    if intent == "JUNK":
        print("Junk message ignored")
        return
    elif intent == "NEW_JD":
        job = extract_job_details(text)
        if job:
            await save_job(job, sender)
            print(f"Saved: {job.company_name} - {job.role}")
            await send_message(
                sender,
                f"Got it! Saved *{job.company_name}* - *{job.role}*\n"
                f"Deadline: {job.deadline}\n"
                f"Stipend: {job.stipend}\n"
                f"Format: {job.work_format}\n"
                f"Apply: {job.apply_link}"
            )
        else:
            print("Extraction failed")
            await send_message(sender, "Sorry, I could not extract job details from that message. Try forwarding the full JD.")
    elif intent == "UPDATE":
        if keyword:
            existing = await get_recent_job_by_keyword(keyword, sender)
            if existing:
                updated = extract_job_details(text)
                if updated:
                    await update_job(existing["_id"], updated)
                    print(f"Updated record for {keyword}")
            else:
                print(f"No existing record found for: {keyword}")
