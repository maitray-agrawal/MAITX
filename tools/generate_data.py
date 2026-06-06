from groq import Groq
from dotenv import load_dotenv
load_dotenv()
import os, json, time

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

companies = [
    "TCS", "Infosys", "Wipro", "Accenture", "Cognizant",
    "HCL", "Tech Mahindra", "Capgemini", "IBM", "Microsoft",
    "Google", "Amazon", "Flipkart", "Zomato", "Swiggy",
    "Paytm", "HDFC Bank", "ICICI Bank", "Deloitte", "EY"
]

roles = [
    "Software Engineer Intern", "Data Science Intern",
    "ML Engineer Intern", "DevOps Intern", "Cloud Intern",
    "Backend Developer Intern", "Frontend Developer Intern",
    "Full Stack Intern", "Cybersecurity Intern", "AI Intern"
]

def generate_message(company, role):
    prompt = f"""Generate a realistic Indian college TnP (Training and Placement) cell WhatsApp message for:
Company: {company}
Role: {role}

Include: company name, role, stipend (in INR), deadline, work location, WFH/WFO, eligibility (BE/BTech branches and batch year), apply link (make up a realistic URL), and a brief company description.

Make it look like a real TnP cell broadcast message. Use formatting with || or bullet points like real TnP messages."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.8
    )
    return response.choices[0].message.content

def generate_label(message):
    prompt = f"""Extract job details from this TnP message and return ONLY a JSON object with these keys:
company_name, role, apply_link, deadline, stipend, work_format, eligibility, location

Message:
{message}"""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
        response_format={"type": "json_object"}
    )
    return response.choices[0].message.content

if __name__ == "__main__":
    os.makedirs("data", exist_ok=True)

    # Load existing data
    try:
        with open("data/training_data.json") as f:
            training_data = json.load(f)
    except:
        training_data = []

    print(f"Starting with {len(training_data)} examples")
    target = 500

    import random
    pairs = [(c, r) for c in companies for r in roles]
    random.shuffle(pairs)

    for i, (company, role) in enumerate(pairs):
        if len(training_data) >= target:
            break
        try:
            print(f"Generating {i+1}: {company} - {role}")
            message = generate_message(company, role)
            label = generate_label(message)
            training_data.append({
                "input": f"Extract job details from this text:\n{message}",
                "output": label
            })
            with open("data/training_data.json", "w") as f:
                json.dump(training_data, f, indent=2)
            time.sleep(2)  # avoid rate limit
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)

    print(f"Generated {len(training_data)} total examples")