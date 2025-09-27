from aiohttp import ClientTimeout
import logging

ROLE_USER = "user"
BACKEND_BASE_URL = "http://localhost:8000"
BACKEND_USER_ENDPOINT = "user"
BACKEND_QUERY_ENDPOINT = "query"
BACKEND_HEADER_LANGUAGE = "Accept-Language"
BACKEND_REQUEST_TIMEOUT = 20000
DOCKER_BASE_URL = "http://localhost:2375"
DOCKER_CONTAINER_ENDPOINT = "containers/{container}/stats"
DOCKER_SERVICES = [
    "chatbot",
    "backend",
    "database",
    "vector_database"
]
QUESTIONS_RAG = [
    "Why am I afraid of spiders? What can I do about it?",
    "I am afraid of getting old. How can I deal with it?",
]
QUESTIONS_OTHER = [
    "Why is Earth the shape of a sphere?",
    "What time is it?"
]
CLIENT_TIMEOUT_CONFIG = ClientTimeout(
    total=100,
    connect=100,
    sock_connect=100,
    sock_read=100
)
DEFAULT_OUTPUT_FILENAME = "test_results.tsv"
DEFAULT_OUTPUT_FILE_WRITE_MODE = "w"
LOG_LEVEL = logging.DEBUG
LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
LOG_FILE = "log.log"