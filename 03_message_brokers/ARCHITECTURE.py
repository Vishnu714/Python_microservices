"""
CELERY ARCHITECTURE DIAGRAM
===========================

The complete flow of how Celery processes tasks.
"""

architecture_diagram = """

╔══════════════════════════════════════════════════════════════════════════════╗
║                        CELERY ARCHITECTURE                                  ║
╚══════════════════════════════════════════════════════════════════════════════╝


1. REQUEST SUBMISSION
====================

Client (Browser/curl)
        │
        │ POST /tasks/email
        ▼
┌───────────────────┐
│   FastAPI App     │
│  (main.py)        │
└───────────────────┘
        │
        │ send_email.delay(email, subject, msg)
        ▼


2. MESSAGE BROKER (Redis)
========================

┌─────────────────────────────────────────────────────────┐
│                    REDIS BROKER                         │
│                                                         │
│  Queues:                                                │
│  ┌─────────────────────────────────────────────────┐   │
│  │ Queue: celery                                   │   │
│  │ ┌─────────────────────────────────────────────┐ │   │
│  │ │ Task: send_email (ID: abc123)               │ │   │
│  │ │ Args: [email, subject, message]             │ │   │
│  │ └─────────────────────────────────────────────┘ │   │
│  │ ┌─────────────────────────────────────────────┐ │   │
│  │ │ Task: process_image (ID: def456)            │ │   │
│  │ │ Args: [image_path, operation]               │ │   │
│  │ └─────────────────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Queue: emails (high priority)                          │
│  Queue: images (medium priority)                        │
│  Queue: compute (low priority)                          │
│                                                         │
└─────────────────────────────────────────────────────────┘
        ▲                           ▼
        │                           │
   Poll              Result Backend (Redis)
   every             ┌──────────────────────┐
   second            │ Task Results         │
        │            │ ┌────────────────────┐
        │            │ │ Task: abc123       │
        │            │ │ Status: SUCCESS    │
        │            │ │ Result: {...}      │
        │            │ └────────────────────┘
        │            │ ┌────────────────────┐
        │            │ │ Task: def456       │
        │            │ │ Status: PROCESSING │
        │            │ │ Progress: 60%      │
        │            │ └────────────────────┘
        │            └──────────────────────┘
        │                           ▲
        │                           │
    ┌───────────────────┐      Stores
    │  Celery Worker    │      Results
    │  (worker.py)      │
    │                   │
    │  Process:         │
    │  1. Poll Redis    │
    │  2. Get task      │
    │  3. Execute       │
    │  4. Store result  │
    └───────────────────┘


3. COMPLETE REQUEST-RESPONSE CYCLE
==================================

    ┌─────────────────────────────────────────────────────────┐
    │ CLIENT sends:                                           │
    │ POST /tasks/email                                       │
    │ {"email": "user@example.com",                           │
    │  "subject": "Hello",                                    │
    │  "message": "Test"}                                     │
    └─────────────────────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │ FASTAPI:                                                │
    │ 1. Parse & validate request (100ms)                     │
    │ 2. Call: send_email.delay(...)                          │
    │ 3. Serialize to JSON                                    │
    │ 4. Send to Redis (10ms)                                 │
    │ 5. Return immediately with task_id ✓                    │
    └─────────────────────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │ REDIS BROKER:                                           │
    │ - Stores: {                                             │
    │     "task": "tasks.send_email",                         │
    │     "id": "abc123def456",                               │
    │     "args": ["user@example.com", "Hello", "Test"],      │
    │     "kwargs": {},                                       │
    │     "retries": 0                                        │
    │   }                                                     │
    └─────────────────────────────────────────────────────────┘
                         │
                         ▼
    ┌─────────────────────────────────────────────────────────┐
    │ CLIENT receives:                                        │
    │ {                                                       │
    │   "task_id": "abc123def456",                            │
    │   "status": "queued",                                   │
    │   "message": "Task queued..."                           │
    │ }                                                       │
    │                                                         │
    │ ⏱ Elapsed time: ~110ms (immediate response!)            │
    └─────────────────────────────────────────────────────────┘
                         │ (user gets response immediately)
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼ (async)                     ▼
    ┌─────────────┐              ┌────────────────────┐
    │ CELERY      │              │ CLIENT can:        │
    │ WORKER      │              │ - Continue work    │
    │             │              │ - Check status     │
    │ Processing: │              │ - Do other things  │
    │ 1. Receive  │              │                    │
    │ 2. Validate │              │ (No waiting!)      │
    │ 3. Execute  │              └────────────────────┘
    │ 4. Retry x3 │
    │ 5. Store    │
    │             │
    │ Time: ~2s   │
    └─────────────┘
          │
          ▼
    ┌─────────────────────────────────────────────────────────┐
    │ REDIS RESULT BACKEND:                                   │
    │ {                                                       │
    │   "abc123def456": {                                      │
    │     "status": "SUCCESS",                                │
    │     "result": {                                         │
    │       "status": "success",                              │
    │       "email": "user@example.com",                      │
    │       "timestamp": "2024-01-29 10:30:45"                │
    │     }                                                   │
    │   }                                                     │
    │ }                                                       │
    └─────────────────────────────────────────────────────────┘
                         ▲
                         │
    ┌─────────────────────────────────────────────────────────┐
    │ CLIENT checks status:                                   │
    │ GET /tasks/abc123def456                                 │
    │                                                         │
    │ Response:                                               │
    │ {                                                       │
    │   "task_id": "abc123def456",                            │
    │   "status": "SUCCESS",                                  │
    │   "result": {...},                                      │
    │   "error": null                                         │
    │ }                                                       │
    └─────────────────────────────────────────────────────────┘


4. TASK STATE MACHINE
====================

                 ┌──────────┐
                 │ PENDING  │ ← Task created, waiting in queue
                 └──────────┘
                      │
                      ▼
                 ┌──────────┐
                 │ STARTED  │ ← Worker picked up task
                 └──────────┘
                      │
          ┌───────────┼───────────┐
          │           │           │
    FAILURE/RETRY   SUCCESS    TIMEOUT
          │           │           │
          ▼           ▼           ▼
      ┌──────┐   ┌─────────┐  ┌──────┐
      │RETRY │   │ SUCCESS │  │FAILURE│
      └──────┘   └─────────┘  └──────┘
          │                       │
          └───────────┬───────────┘
                      ▼
                 ┌──────────┐
                 │ REVOKED  │ ← Task cancelled
                 └──────────┘
                 (optional)


5. WORKER POOL & CONCURRENCY
============================

Single Worker (1 process, 4 threads):
    ┌─────────────────────────────────┐
    │ Worker Process                  │
    │ ┌─────┬─────┬─────┬─────┐       │
    │ │Task │Task │Task │Task │       │
    │ │ 1   │ 2   │ 3   │ 4   │       │
    │ │     │     │     │     │       │
    │ │Exec │Exec │Exec │Wait │       │
    │ └─────┴─────┴─────┴─────┘       │
    └─────────────────────────────────┘


Multiple Workers (for scaling):
    ┌──────────────────────────────────┐
    │        REDIS BROKER              │
    │      [pending tasks]             │
    └──────────────────────────────────┘
     │            │              │
     ▼            ▼              ▼
  ┌──────┐   ┌──────┐       ┌──────┐
  │ W1   │   │ W2   │  ...  │ W-N  │
  │ 4    │   │ 4    │       │ 4    │
  │ jobs │   │ jobs │       │ jobs │
  └──────┘   └──────┘       └──────┘
    
  Total capacity: N workers × 4 concurrent = 4N parallel tasks


6. COMPARISON: WITH vs WITHOUT CELERY
====================================

WITHOUT CELERY (Synchronous):
    Request → Process (2s) → Response
    Client waits ❌
    1 request/2s per worker

WITH CELERY (Asynchronous):
    Request → Queue (10ms) → Response ✓
    Client gets response immediately
    Worker processes in background
    1000 requests/second can all respond instantly


Key differences:
    
    Metric              Without Celery    With Celery
    ──────────────────────────────────────────────────
    Response time       2000ms            110ms
    User experience     Waiting...        Instant ✓
    Server load         High (blocked)    Low (async)
    Scalability         Difficult         Easy
    Error handling      Lost on timeout   Retry logic ✓
    Task retry          Manual code       Built-in ✓
    Task scheduling     Manual cron       Built-in ✓
    Rate limiting       Manual            Built-in ✓


═══════════════════════════════════════════════════════════════════════════════
"""

print(architecture_diagram)
