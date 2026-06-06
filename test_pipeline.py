import asyncio
from dotenv import load_dotenv
load_dotenv()

from app.router_agent import classify_and_process

test_message = """
Hiring Alert! Infosys is hiring for SDE Intern role.
Apply at https://infosys.com/careers
Deadline: 5th June 2026
Stipend: 25000/month
Work from Office - Pune
Eligibility: BE/BTech CS/IT students only
"""

asyncio.run(classify_and_process(test_message, "919999999999"))