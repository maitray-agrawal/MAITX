from pydantic import BaseModel
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
    prompt = f"""You are a strict JSON extractor. Extract internship/job details from the text below.
Return ONLY a valid JSON object with these exact keys:
company_name, role, apply_link, deadline, stipend, work_format, eligibility, location, extra_notes.
If a field is not present, return null for that field.
Do NOT add any explanation. Return ONLY the JSON object.

Text:
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
        data = json.loads(raw)
        return JobRecord(**data)
    except Exception as e:
        print(f"Extraction parsing error: {e}")
        print(f"Raw response: {raw}")
        return None
