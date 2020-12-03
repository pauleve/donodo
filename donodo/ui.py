import sys

import logging

logger = logging.getLogger("donodo")
logger.setLevel(logging.INFO)

def error(*args, **kwargs):
    logger.error(*args, **kwargs)
    sys.exit(1)

info = logger.info
debug = logger.debug
