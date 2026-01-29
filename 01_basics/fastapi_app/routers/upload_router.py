# routers/upload_router.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from services.upload_service import process_upload, get_job_status, delete_job, get_all_jobs
from schemas.upload_schema import UploadResponse, UserInfo, JobStatus, DeleteResponse
from typing import List

router = APIRouter()

@router.post("/upload", response_model=UploadResponse)
async def upload_file(file: UploadFile = File(...), user_id: str = None, user_email: str = None):
    try:
        if not user_id or not user_email:
            raise HTTPException(status_code=400, detail="user_id and user_email are required")
        job_id = await process_upload(file, user_id, user_email)
        return UploadResponse(job_id=job_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    job = await get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job

@router.delete("/delete/{job_id}", response_model=DeleteResponse)
async def delete_upload(job_id: str):
    deleted = await delete_job(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Job not found")
    return DeleteResponse(message="File deleted successfully", deleted=True)

@router.get("/uploads", response_model=List[JobStatus])
async def list_all_uploads():
    jobs = await get_all_jobs()
    return jobs