import sys
import platform
from celery_app import app


def is_windows_os() -> bool:
    """
    Detect whether the current OS is Windows.
    Celery multiprocessing (prefork) is unstable on Windows,
    so we must use the 'solo' pool.
    """
    return platform.system().lower().startswith("win")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("CELERY WORKER STARTED")
    print(f"Broker: {app.conf.broker_url}")
    print(f"Platform: {platform.system()}")
    print("=" * 60 + "\n")

    if is_windows_os():
        print("⚠ Windows detected → using SOLO worker pool\n")

        worker_args = [
            "worker",
            "--loglevel=info",
            "--pool=solo",
            "--concurrency=1",
            "--time-limit=1800",
        ]
    else:
        print("✅ Unix system detected → using PREFORK worker pool\n")

        worker_args = [
            "worker",
            "--loglevel=info",
            "--concurrency=4",
            "--time-limit=1800",
        ]

    app.worker_main(argv=worker_args)
