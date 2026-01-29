"""
QUICK START: Run Everything in 5 Minutes
=========================================
"""

print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                    CELERY + FASTAPI QUICK START                           ║
╚════════════════════════════════════════════════════════════════════════════╝

PREREQUISITES:
==============
✓ Python 3.8+
✓ Redis running (or RabbitMQ)


STEP 1: INSTALL DEPENDENCIES
============================
In VS Code Terminal:

    pip install celery redis fastapi uvicorn


STEP 2: START REDIS
===================
In Terminal 1:
    
    redis-server
    
Or if using Docker:
    
    docker run -p 6379:6379 redis:latest

Check it's running:
    redis-cli ping
    # Should return: PONG


STEP 3: START FASTAPI SERVER
=============================
In Terminal 2:

    cd 02_celery
    python main.py
    
    # Or with auto-reload:
    uvicorn main:app --reload --port 8000

Expected output:
    Uvicorn running on http://127.0.0.1:8000
    
Visit: http://localhost:8000 to see API endpoints


STEP 4: START CELERY WORKER
============================
In Terminal 3:

    cd 02_celery
    python worker.py
    
Expected output:
    ==============================
    CELERY WORKER STARTED
    Broker: redis://localhost:6379/0
    Backend: redis://localhost:6379/0
    ==============================
    [tasks] Waiting for tasks...


STEP 5: TEST THE SYSTEM
=======================

Test 1 - Send Email Task (with retries):
    curl -X POST "http://localhost:8000/tasks/email" \\
      -H "Content-Type: application/json" \\
      -d '{
        "email": "user@example.com",
        "subject": "Hello Celery",
        "message": "Testing async tasks"
      }'
    
    Save the task_id from response, e.g.: "abc123def456"


Test 2 - Check Status:
    curl "http://localhost:8000/tasks/abc123def456"
    
    You'll see:
    - status: "PENDING" → "STARTED" → "SUCCESS"
    - result: null (until complete)


Test 3 - Heavy Computation with Progress:
    curl -X POST "http://localhost:8000/tasks/compute" \\
      -H "Content-Type: application/json" \\
      -d '{"iterations": 100}'
    
    Then check status with GET /tasks/{task_id}
    You'll see progress: {"current": 50, "total": 100, "percent": 50.0}


Test 4 - Cancel a Task:
    curl -X DELETE "http://localhost:8000/tasks/abc123def456"
    
    Status will change to "REVOKED"


Test 5 - Batch Multiple Tasks:
    curl -X POST "http://localhost:8000/tasks/batch"
    
    Creates 3 email tasks at once


Test 6 - Task Chaining (Workflow):
    curl -X POST "http://localhost:8000/tasks/chain-report?data_id=123"
    
    Task 1: generate_report(123) → Task 2: send_report(result)


Test 7 - Monitor Workers:
    curl "http://localhost:8000/celery/stats"
    curl "http://localhost:8000/celery/active-tasks"


✅ YOU'RE RUNNING CELERY!
========================


UNDERSTANDING WHAT HAPPENED:
============================

1. FastAPI Server (Terminal 2):
   - Listens on http://localhost:8000
   - Receives HTTP requests
   - Queues tasks to Redis
   - Returns task_id immediately (doesn't wait)
   
2. Redis (Terminal 1):
   - Stores pending tasks (broker)
   - Stores task results (backend)
   - Acts as message queue
   
3. Celery Worker (Terminal 3):
   - Continuously polls Redis for tasks
   - Executes tasks when found
   - Stores results back to Redis
   - Can run multiple workers for parallelism

Flow:
    Browser → FastAPI → Redis → Celery Worker → Results back to Redis


WHAT'S HAPPENING BEHIND THE SCENES:
===================================

When you POST to /tasks/email:
    
    1. FastAPI receives request
    2. Calls: send_email.delay(email, subject, message)
    3. This serializes the task to JSON: {
         "task": "tasks.send_email",
         "id": "abc123...",
         "args": ["user@example.com", "Subject", "Message"]
       }
    4. Sends to Redis broker
    5. Returns task_id immediately to client
    6. Returns 200 OK without waiting
    
Meanwhile in Worker:
    
    7. Worker polls Redis every second
    8. Finds the task
    9. Deserializes and executes: send_email("user@example.com", ...)
    10. Task runs for ~2 seconds (with retries on failure)
    11. Stores result in Redis
    
Client checks status:
    
    12. GET /tasks/abc123 queries Redis
    13. Finds result
    14. Returns status and data


WHY THIS IS POWERFUL:
====================

WITHOUT Celery:
    POST /send-email
    ├─ Validate input (100ms)
    ├─ Connect to SMTP server (500ms)
    ├─ Send email (2000ms)
    ├─ Wait for response
    └─ Return after 2.6 seconds
    
    Client waits 2.6 seconds ❌
    If 100 concurrent requests → server needs 260 seconds total ❌

WITH Celery:
    POST /tasks/email
    ├─ Validate input (100ms)
    ├─ Queue to Redis (10ms)
    └─ Return immediately after 110ms ✅
    
    Client gets response instantly
    Worker processes in background
    100 concurrent requests still complete instantly ✅


NEXT STEPS:
===========

1. Read through the code in:
   - celery_app.py (configuration)
   - tasks.py (task definitions)
   - main.py (FastAPI integration)

2. Understand the patterns in:
   - advanced_patterns.py (production ready)
   - CELERY_GUIDE.md (comprehensive reference)

3. Modify tasks for your use case:
   - Email sending
   - Image processing
   - Data analysis
   - External API calls
   - PDF generation

4. Scale with:
   - Multiple workers: celery -A celery_app worker -c 8
   - Task routing: separate queues for different task types
   - Celery Beat: scheduled periodic tasks


TROUBLESHOOTING:
================

Issue: Worker shows "No registered tasks"
Solution: Make sure to import tasks before starting worker

Issue: "Connection refused" error
Solution: Make sure Redis is running on localhost:6379

Issue: Tasks stuck as PENDING
Solution: Check worker is running and connected to Redis

Issue: Memory keeps growing
Solution: Reduce prefetch_multiplier or number of workers


REFERENCES:
===========
- Celery Docs: https://docs.celeryproject.io/
- Redis Docs: https://redis.io/docs/
- FastAPI Docs: https://fastapi.tiangolo.com/
- This Guide: See CELERY_GUIDE.md in this directory


═══════════════════════════════════════════════════════════════════════════════
                        Happy async task processing! 🚀
═══════════════════════════════════════════════════════════════════════════════
""")
