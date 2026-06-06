import json
import os
from dotenv import load_dotenv

load_dotenv()

from app.database import jobs_collection

def main():
    jobs = list(jobs_collection.find({}))

    training = []

    for job in jobs:
        training.append({
            "input": f"""
Extract job details:
Company: {job.get('company_name')}
Role: {job.get('role')}
Deadline: {job.get('deadline')}
Stipend: {job.get('stipend')}
Location: {job.get('location')}
Format: {job.get('work_format')}
Eligibility: {job.get('eligibility')}
Link: {job.get('apply_link')}
""",
            "output": json.dumps({
                "company_name": job.get("company_name"),
                "role": job.get("role"),
                "deadline": job.get("deadline"),
                "stipend": job.get("stipend"),
                "work_format": job.get("work_format"),
                "eligibility": job.get("eligibility"),
                "location": job.get("location"),
                "apply_link": job.get("apply_link")
            })
        })

    os.makedirs("data", exist_ok=True)

    with open("data/training_data.json", "w", encoding="utf-8") as f:
        json.dump(training, f, indent=2)

    print(f"Exported {len(training)} examples")

if __name__ == "__main__":
    main()