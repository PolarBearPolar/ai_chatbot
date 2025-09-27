import os
import logging
from aiohttp import ClientTimeout

API_HOST = "0.0.0.0"
API_PORT = 8000
API_HEADER_LANGUAGE = "Accept-Language"
API_DEFAULT_LANGUAGE = "en"
CHATBOT_URL = f"http://chatbot:{os.environ.get('CHATBOT_PORT')}"
CHATBOT_REQUEST_TIMEOUT = 20000
DATABASE_URL = f"postgresql+psycopg://{os.environ.get('POSTGRES_USER')}:{os.environ.get('POSTGRES_PASSWORD')}@database:{os.environ.get('POSTGRES_PORT')}/{os.environ.get('POSTGRES_DB')}"
ROLE_ASSISTANT = "ASSISTANT"
IS_RAG_USED = os.environ.get('IS_RAG_USED', 'false').lower() == 'true'
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
LOG_FILE = "log.log"
CLIENT_TIMEOUT_CONFIG = ClientTimeout(
    total=500,
    connect=500,
    sock_connect=500,
    sock_read=500
)
