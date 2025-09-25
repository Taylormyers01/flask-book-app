import logging
import os
import tempfile
from datetime import datetime
from logging.handlers import RotatingFileHandler

# Configure the root logger
logger = logging.getLogger("book-flask")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

# StreamHandler (console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

today_date = datetime.today().strftime('%Y%m%d')

log_output = tempfile.NamedTemporaryFile(delete=False, prefix='book_app', suffix=today_date +".log")
# print(os.getcwd())

# FileHandler (logs/app.log)
file_handler = RotatingFileHandler(log_output.name, maxBytes=1000000, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
