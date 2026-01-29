# services/upload_service.py
import os
import uuid
import asyncio
from fastapi import UploadFile
from pathlib import Path

UPLOAD_DIR = "uploads"
JOBS_DB = {}

# Ensure upload directory exists
Path(UPLOAD_DIR).mkdir(exist_ok=True)

async def process_upload(file: UploadFile, user_id: str, user_email: str):
    job_id = str(uuid.uuid4())
    file_path = os.path.join(UPLOAD_DIR, job_id, file.filename)
    
    # Create job directory
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    # Save file
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    # Store job metadata
    JOBS_DB[job_id] = {
        "job_id": job_id,
        "filename": file.filename,
        "user_id": user_id,
        "user_email": user_email,
        "file_path": file_path,
        "status": "completed",
        "file_size": len(contents)
    }
    
    return job_id

async def get_job_status(job_id: str):
    if job_id not in JOBS_DB:
        return None
    return JOBS_DB[job_id]

async def get_all_jobs():
    return list(JOBS_DB.values())

async def delete_job(job_id: str):
    if job_id not in JOBS_DB:
        return False
    
    job = JOBS_DB[job_id]
    file_path = job["file_path"]
    
    # Delete file
    if os.path.exists(file_path):
        os.remove(file_path)
    
    # Remove job directory if empty
    job_dir = os.path.dirname(file_path)
    if os.path.exists(job_dir) and not os.listdir(job_dir):
        os.rmdir(job_dir)
    
    # Remove from database
    del JOBS_DB[job_id]
    return True