# MAITX — TnP Internship Tracker

An Agentic AI pipeline that eliminates missed placement opportunities.

## What it does
- Ingests unstructured TnP WhatsApp messages and PDFs
- Extracts structured job data (company, role, deadline, stipend, link)
- Saves to MongoDB Atlas
- Sends automated 48-hour deadline reminders via WhatsApp

## Tech Stack
- **Backend:** FastAPI, Python
- **AI:** Google Gemini 2.5 Flash
- **Database:** MongoDB Atlas
- **Messaging:** WhatsApp Business API (Meta)
- **Scheduler:** APScheduler

## Architecture
WhatsApp → FastAPI Webhook → Router Agent → Extractor Agent → MongoDB → Scheduler → WhatsApp Reminder

## Setup
1. Clone the repo
2. Create virtual environment: `python -m venv venv`
3. Install dependencies: `pip install -r requirements.txt`
4. Create `.env` file with your API keys (see `.env.example`)
5. Run: `python run.py`

## Environment Variables
Create a `.env` file with:
```
VERIFY_TOKEN=your_verify_token
WHATSAPP_TOKEN=your_meta_token
PHONE_NUMBER_ID=your_phone_number_id
GEMINI_API_KEY=your_gemini_key
MONGO_URI=your_mongodb_uri
```