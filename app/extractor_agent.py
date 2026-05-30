from pydantic import BaseModel
from typing import Optional
from google import genai
import os
import json

_client = None

def get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client


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
    prompt = f"""You are a strict JSON extractor. Extract internship/job details from the text below.
Return ONLY a valid JSON object with these exact keys:
company_name, role, apply_link, deadline, stipend, work_format, eligibility, location, extra_notes.
If a field is not present, return null for that field.
Do NOT add any explanation. Return ONLY the JSON object.

Text:
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
        data = json.loads(raw.strip())
        return JobRecord(**data)
    except Exception as e:
        print(f"Extraction parsing error: {e}")
        print(f"Raw response: {raw}")
        return None
