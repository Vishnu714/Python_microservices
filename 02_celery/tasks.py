from celery_app import app
import time


@app.task(bind=True)
def send_email(self, email: str, subject: str, body: str):
    time.sleep(2)
    return {"status": "sent", "email": email}


@app.task(bind=True)
def process_data(self, data_id: int):
    total = 100
    for i in range(total):
        time.sleep(0.05)
        self.update_state(
            state="PROGRESS",
            meta={
                "current": i + 1,
                "total": total,
                "percent": int((i + 1) / total * 100),
            },
        )
    return {"status": "complete", "data_id": data_id}


@app.task
def generate_report(report_id: str):
    time.sleep(1)
    return {"status": "generated", "report_id": report_id}
