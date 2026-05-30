from fastapi import APIRouter, Request, BackgroundTasks
from fastapi.responses import PlainTextResponse
from app.router_agent import classify_and_process
import os

router = APIRouter()


@router.get("/webhook")
async def verify_webhook(request: Request):
    params = request.query_params
    hub_mode = params.get("hub.mode")
    hub_challenge = params.get("hub.challenge")
    hub_verify_token = params.get("hub.verify_token")
    verify_token = "my_secret_token"

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
        message = changes["messages"][0]
        text = message["text"]["body"]
        sender = message["from"]
        print(f"Message from {sender}: {text[:80]}...")
        background_tasks.add_task(classify_and_process, text, sender)
    except (KeyError, IndexError):
        print("Non-message event received, ignoring")
    return {"status": "ok"}
