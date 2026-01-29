"""
Celery + FastAPI Microservices Example

This package contains a complete Celery setup integrated with FastAPI,
demonstrating async task processing from basics to production-ready patterns.

Structure:
- celery_app.py: Celery configuration
- tasks.py: Task definitions
- worker.py: Worker script
- main.py: FastAPI integration with endpoints
- advanced_patterns.py: Production patterns
- CELERY_GUIDE.md: Complete guide with examples
"""

from .celery_app import app as celery_app

__all__ = ["celery_app"]
