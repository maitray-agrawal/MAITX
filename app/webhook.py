from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.router_agent import classify_and_process
from app.pdf_handler import download_and_extract_pdf
from app.database import users_collection
from app.whatsapp import send_message
import os
import re

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)


@router.get("/webhook")
async def verify_webhook(request: Request):
    query = str(request.url.query)
    params = {}
    for part in query.split("&"):
        if "=" in part:
            k, v = part.split("=", 1)
            from urllib.parse import unquote_plus
            params[unquote_plus(k)] = unquote_plus(v)

    hub_mode = params.get("hub.mode")
    hub_challenge = params.get("hub.challenge")
    hub_verify_token = params.get("hub.verify_token")
    verify_token = os.getenv("VERIFY_TOKEN", "my_secret_token")

    print(f"Meta attempt | mode={hub_mode} | token={hub_verify_token}")

    if hub_mode == "subscribe" and hub_verify_token == verify_token:
        print("Webhook verified by Meta")
        return PlainTextResponse(content=hub_challenge, status_code=200)

    print("Verification failed")
    return PlainTextResponse(content="Forbidden", status_code=403)


@router.post("/webhook")
@limiter.limit("20/minute")
async def receive_message(request: Request, background_tasks: BackgroundTasks):
    payload = await request.json()

    try:
        changes = payload["entry"][0]["changes"][0]["value"]
        messages = changes.get("messages", [])

        if not messages:
            print("Non-message event received, ignoring")
            return {"status": "ok"}

        message = messages[0]
        sender = message["from"]
        msg_type = message.get("type")

        print(f"Message type: {msg_type} from {sender}")

        if msg_type == "text":
            text = message["text"]["body"].strip()
            print(f"Text message: {text[:80]}...")
            background_tasks.add_task(handle_text_message, text, sender)

        elif msg_type == "document":
            doc = message.get("document", {})
            mime_type = doc.get("mime_type", "")
            filename = doc.get("filename", "unknown")
            media_id = doc.get("id")

            print(f"Document received: {filename} ({mime_type})")

            if "pdf" in mime_type.lower():
                background_tasks.add_task(
                    process_pdf_message, media_id, sender, filename, mime_type
                )
            elif "word" in mime_type.lower() or "docx" in mime_type.lower() or "document" in mime_type.lower():
                background_tasks.add_task(
                    process_pdf_message, media_id, sender, filename, mime_type
                )
            else:
                print(f"Unsupported document type: {mime_type}, ignoring")

        else:
            print(f"Unsupported message type: {msg_type}, ignoring")

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error: {e}")

    return {"status": "ok"}


async def handle_text_message(text: str, sender: str):
    user = users_collection.find_one({"phone": sender})

    if not user:
        users_collection.insert_one({"phone": sender, "email": None, "onboarding": True})
        await send_message(
            sender,
            "👋 Welcome to MAITX TnP Tracker!\n\nPlease reply with your college email address to complete setup and access your dashboard."
        )
        return

    if user.get("onboarding") and not user.get("email"):
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(email_pattern, text):
            users_collection.update_one(
                {"phone": sender},
                {"$set": {"email": text.lower(), "onboarding": False}}
            )
            await send_message(
                sender,
                f"✅ Setup complete! Your email *{text}* is linked.\n\nYou can now login at maitx.vercel.app with this email.\n\nForward TnP job messages here and they'll appear on your dashboard!"
            )
        else:
            await send_message(
                sender,
                "That doesn't look like a valid email. Please reply with your college email address (e.g. name@college.edu)"
            )
        return

    await classify_and_process(text, sender)


async def process_pdf_message(media_id: str, sender: str, filename: str, mime_type: str = "application/pdf"):
    print(f"Processing document: {filename} ({mime_type}) from {sender}")
    media_url = f"https://graph.facebook.com/v18.0/{media_id}"
    text = download_and_extract_pdf(media_url, mime_type)
    if not text:
        await send_message(
            sender,
            "Sorry, could not read that file. Please send job details as text."
        )
        return
    await classify_and_process(text, sender)
