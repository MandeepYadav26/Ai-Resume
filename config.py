import os

# Default Application Configuration
PORT = 5000
HOST = "127.0.0.1"
DEBUG = True

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB upload limit
