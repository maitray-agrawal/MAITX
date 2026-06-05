from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.webhook import router as webhook_router
from app.api import router as api_router
from app.auth_routes import router as auth_router
from app.admin_routes import router as admin_router
from app.scheduler import start_scheduler

limiter = Limiter(key_func=get_remote_address)

app = FastAPI(title="TnP Tracker - MAITX")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhook_router)
app.include_router(api_router)
app.include_router(auth_router)
app.include_router(admin_router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print("TnP Tracker MAITX running")

@app.get("/")
async def root():
    return {"status": "MAITX TnP Tracker is live"}

@app.get("/debug/env")
async def debug_env():
    import os
    key = os.getenv("FAST2SMS_KEY", "NOT SET")
    return {"key_length": len(key), "key_preview": key[:6] + "..." if len(key) > 6 else "TOO SHORT"}

@app.get("/debug/env")
async def debug_env():
    import os
    key = os.getenv("FAST2SMS_KEY", "NOT SET")
    return {"key_length": len(key), "key_preview": key[:6] + "..." if len(key) > 6 else "TOO SHORT"}
