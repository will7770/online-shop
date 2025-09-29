# Main config options
#####################
bind = '0.0.0.0:8000'
backlog = 1024

workers = 4
worker_class = 'gthread'
threads = '3'

worker_connections = 100
max_requests = 1000
max_requests_jitter = 100
timeout = 30
graceful_timeout = 30
keepalive = 10


# Hooks
#######################
def on_starting(server):
    print("--- Gunicorn initiated ---")

def post_fork(server, worker):
    print(f"-- Worker {worker.pid} listening for requests --")
