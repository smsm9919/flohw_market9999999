# Gunicorn Production Configuration for Flohmarkt
import os
import multiprocessing

# Server Socket
bind = "0.0.0.0:5000"
backlog = 2048

# Worker Processes
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "gthread"
worker_connections = 1000
threads = 4
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2

# Logging
accesslog = "-"
errorlog = "-"
loglevel = "info"
access_log_format = '%(h)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s" "%(a)s" %(D)s'

# Process naming
proc_name = "flohmarkt-production"

# Server mechanics
daemon = False
pidfile = "/tmp/gunicorn.pid"
user = None
group = None
tmp_upload_dir = None

# SSL (handled by Render)
keyfile = None
certfile = None

# Environment
forwarded_allow_ips = "*"
secure_scheme_headers = {
    'X-FORWARDED-PROTOCOL': 'ssl',
    'X-FORWARDED-PROTO': 'https',
    'X-FORWARDED-SSL': 'on'
}

# Performance tuning
worker_tmp_dir = "/dev/shm"  # Use memory for worker temp files

# Graceful shutdown
graceful_timeout = 30

# Memory management
max_worker_memory = 200 * 1024 * 1024  # 200MB per worker

def when_ready(server):
    server.log.info("Flohmarkt server ready on https://flowmarket.com")

def worker_init(worker):
    worker.log.info(f"Worker {worker.pid} initialized")

def pre_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def post_fork(server, worker):
    server.log.info(f"Worker spawned (pid: {worker.pid})")

def worker_exit(server, worker):
    server.log.info(f"Worker {worker.pid} exited")

def on_exit(server):
    server.log.info("Flohmarkt server shutting down")