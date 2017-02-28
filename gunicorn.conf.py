import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

bind = 'localhost:8080'
loglevel = 'info'
timeout = 120
graceful_timeout = 60
worker_class = 'gevent'
worker_connections = 10
