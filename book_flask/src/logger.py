import logging
from logging.handlers import RotatingFileHandler

# Configure the root logger
logger = logging.getLogger("book-flask")
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s in %(module)s: %(message)s")

# StreamHandler (console)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

# FileHandler (logs/app.log)
file_handler = RotatingFileHandler("logs/app.log", maxBytes=1000000, backupCount=3)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)
