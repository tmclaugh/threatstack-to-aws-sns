#!/usr/bin/env python

from app import create_app
import logging
from logging.config import fileConfig
import os

dirname = os.path.dirname(__file__)
logging_conf = os.path.join(dirname, 'logging.conf')
fileConfig(logging_conf, disable_existing_loggers=False)
if os.environ.get('TS_DEBUG'):
    logging.root.setLevel(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

# Gunicorn entry point.
application = create_app()

if __name__ == '__main__':
    # Entry point when run via Python interpreter.
    print("== Running in debug mode ==")
    application.run(host='localhost', port=8080, debug=True)
