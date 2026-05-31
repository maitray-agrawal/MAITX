content = """from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.router_agent import classify_and_process
from app.pdf_handler import download_and_extract_pdf
import os
import requests

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    # Read raw query string to handle dot-notation params
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
            text = message["text"]["body"]
            print(f"Text message: {text[:80]}...")
            background_tasks.add_task(classify_and_process, text, sender)

        elif msg_type == "document":
            doc = message.get("document", {})
            mime_type = doc.get("mime_type", "")
            filename = doc.get("filename", "unknown")
            media_id = doc.get("id")
            print(f"Document received: {filename} ({mime_type})")
            if "pdf" in mime_type.lower():
                background_tasks.add_task(
                    process_pdf_message, media_id, sender, filename
                )
        else:
            print(f"Unsupported message type: {msg_type}, ignoring")

    except (KeyError, IndexError) as e:
        print(f"Webhook parse error: {e}")

    return {"status": "ok"}


async def process_pdf_message(media_id: str, sender: str, filename: str):
    print(f"Processing PDF: {filename} from {sender}")
    media_url = f"https://graph.facebook.com/v18.0/{media_id}"
    text = download_and_extract_pdf(media_url)
    if not text:
        from app.whatsapp import send_message
        await send_message(sender, "Sorry, could not read that PDF. Please send as text.")
        return
    await classify_and_process(text, sender)
"""

with open("app/webhook.py", "w", encoding="utf-8") as f:
    f.write(content)
print("webhook.py updated")