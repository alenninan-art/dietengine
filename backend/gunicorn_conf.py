import multiprocessing
import os

bind = f"0.0.0.0:{os.getenv('PORT', '8000')}"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
timeout = 120
graceful_timeout = 30
keepalive = 5
max_requests = int(os.getenv("GUNICORN_MAX_REQUESTS", "200"))
max_requests_jitter = int(os.getenv("GUNICORN_MAX_REQUESTS_JITTER", "25"))
loglevel = "info"
