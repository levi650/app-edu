Background jobs (management command)

This project includes a simple cron-friendly management command to process background jobs without Celery.

How to run once:

```
.venv\Scripts\python.exe manage.py run_background_jobs --once
```

Run continuously (sleep interval 10s):

```
.venv\Scripts\python.exe manage.py run_background_jobs --sleep 10
```

What it does:
- Processes ImportJob objects with status PENDING: opens the uploaded file and runs the same import logic used by the web UI.
- Marks jobs RUNNING → DONE or FAILED and populates `imported_rows`, `failed_rows`, and `errors`.

Notes:
- This is intentionally light-weight for demo/dev. For production, swap to a queue (Celery/RQ) and use worker pools and reliable retries.
