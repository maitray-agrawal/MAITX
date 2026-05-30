from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from app.webhook import router as webhook_router
from app.scheduler import start_scheduler

app = FastAPI(title="TnP Tracker - MAITX")
app.include_router(webhook_router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()
    print("TnP Tracker MAITX running")

@app.get("/")
async def root():
    return {"status": "MAITX TnP Tracker is live"}
