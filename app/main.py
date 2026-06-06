@"
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
from app.resume_routes import router as resume_router
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
app.include_router(resume_router)

@app.on_event("startup")
async def startup_event():
    from app.database import ensure_indexes
    ensure_indexes()
    start_scheduler()
    print("TnP Tracker MAITX running")

@app.get("/")
async def root():
    return {"status": "MAITX TnP Tracker is live"}
"@ | Out-File -Encoding utf8 app\main.py

