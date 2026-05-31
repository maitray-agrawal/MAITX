extractor_content = """from pydantic import BaseModel
from typing import Optional
from groq import Groq
import os
import json

def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


class JobRecord(BaseModel):
    company_name: Optional[str] = None
    role: Optional[str] = None
    apply_link: Optional[str] = None
    deadline: Optional[str] = None
    stipend: Optional[str] = None
    work_format: Optional[str] = None
    eligibility: Optional[str] = None
    location: Optional[str] = None
    extra_notes: Optional[str] = None


def extract_job_details(text: str) -> Optional[JobRecord]:
    prompt = f\"\"\"You are a strict JSON extractor. Extract internship/job details from the text below.
Return ONLY a valid JSON object with these exact keys:
company_name, role, apply_link, deadline, stipend, work_format, eligibility, location, extra_notes.
If a field is not present, return null for that field.
Do NOT add any explanation. Return ONLY the JSON object.

Text:
{text}
\"\"\"
    client = get_client()
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    raw = response.choices[0].message.content.strip()
    try:
        data = json.loads(raw)
        return JobRecord(**data)
    except Exception as e:
        print(f"Extraction parsing error: {e}")
        print(f"Raw response: {raw}")
        return None
"""

router_content = """from groq import Groq
import os
import json
from app.extractor_agent import extract_job_details
from app.database import save_job, get_recent_job_by_keyword, update_job
from app.whatsapp import send_message


def get_client():
    return Groq(api_key=os.getenv("GROQ_API_KEY"))


def classify_message(text: str) -> dict:
    prompt = f\"\"\"
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
\"\"\"
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
        print("Junk message ignored")
        return

    elif intent == "NEW_JD":
        try:
            job = extract_job_details(text)
            if job:
                await save_job(job, sender)
                print(f"Saved: {job.company_name} - {job.role}")
                await send_message(
                    sender,
                    f"Got it! Saved *{job.company_name}* - *{job.role}*\\n"
                    f"Deadline: {job.deadline}\\n"
                    f"Stipend: {job.stipend}\\n"
                    f"Format: {job.work_format}\\n"
                    f"Apply: {job.apply_link}"
                )
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
"""

with open("app/extractor_agent.py", "w", encoding="utf-8") as f:
    f.write(extractor_content)
print("extractor_agent.py updated with Groq")

with open("app/router_agent.py", "w", encoding="utf-8") as f:
    f.write(router_content)
print("router_agent.py updated with Groq")