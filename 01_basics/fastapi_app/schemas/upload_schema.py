# schemas/upload_schema.py
from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    user_id: str
    user_email: str

class UploadResponse(BaseModel):
    job_id: str

class JobStatus(BaseModel):
    job_id: str
    filename: str
    user_id: str
    user_email: str
    status: str
    file_size: int

class DeleteResponse(BaseModel):
    message: str
    deleted: bool