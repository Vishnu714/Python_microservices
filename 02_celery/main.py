from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, Any
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from celery_app import app as celery_app
from tasks import send_email, process_data, generate_report
from celery.result import AsyncResult

app = FastAPI(title="Celery + FastAPI")

class EmailRequest(BaseModel):
    email: str
    subject: str
    body: str

class DataRequest(BaseModel):
    data_id: int


@app.get("/")
async def root():
    return {
        "message": "Celery + FastAPI",
        "endpoints": {
            "POST /submit/email": "Send email task",
            "POST /submit/data": "Process data task",
            "POST /submit/report": "Generate report task",
            "GET /status/{task_id}": "Check task status",
            "DELETE /tasks/{task_id}": "Cancel task",
        }
    }

@app.post("/submit/email")
async def submit_email(req: EmailRequest):
    task = send_email.delay(req.email, req.subject, req.body)
    return {"task_id": task.id, "status": "queued"}

@app.post("/submit/data")
async def submit_data(req: DataRequest):
    task = process_data.delay(req.data_id)
    return {"task_id": task.id, "status": "queued"}

@app.post("/submit/report")
async def submit_report(report_id: str):
    task = generate_report.delay(report_id)
    return {"task_id": task.id, "status": "queued"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    
    response = {
        "task_id": task_id,
        "status": result.state,
        "result": None,
        "progress": None,
        "error": None,
    }
    
    if result.state == "PROGRESS" and isinstance(result.info, dict):
        response["progress"] = result.info

    elif result.state == "SUCCESS":
        response["result"] = result.result
    elif result.state == "FAILURE":
        response["error"] = str(result.info)
    
    return response

@app.delete("/tasks/{task_id}")
async def cancel_task(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    result.revoke(terminate=True)
    return {"task_id": task_id, "status": "cancelled"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
