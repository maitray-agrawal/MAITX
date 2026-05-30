from fastapi import APIRouter
from app.database import jobs_collection
from bson import ObjectId
import json

router = APIRouter()


def serialize(doc):
    doc["_id"] = str(doc["_id"])
    return doc


@router.get("/api/jobs/{user_id}")
async def get_jobs(user_id: str):
    jobs = list(jobs_collection.find({"user_id": user_id}).sort("created_at", -1))
    return [serialize(j) for j in jobs]


@router.get("/api/jobs/{user_id}/upcoming")
async def get_upcoming_jobs(user_id: str):
    from datetime import datetime, timedelta
    jobs = list(jobs_collection.find({
        "user_id": user_id,
        "notified": False
    }).sort("created_at", -1))
    return [serialize(j) for j in jobs]


@router.patch("/api/jobs/{job_id}/applied")
async def mark_applied(job_id: str):
    jobs_collection.update_one(
        {"_id": ObjectId(job_id)},
        {"$set": {"applied": True}}
    )
    return {"status": "updated"}


@router.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str):
    jobs_collection.delete_one({"_id": ObjectId(job_id)})
    return {"status": "deleted"}
