import os
import logging

BACKEND_BASE_URL = f"http://backend:{os.environ.get('BACKEND_PORT')}"
BACKEND_USER_ENDPOINT = "user"
BACKEND_QUERY_ENDPOINT = "query"
BACKEND_REQUEST_TIMEOUT = 20000
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
LOG_FILE = "log.log"
ROLE_ASSISTANT = "ASSISTANT"
ROLE_USER = "USER"
CHAT_NEWLINE_CHARACTER = "  \n"
GENDER_MALE = "Male"
GENDER_FEMALE = "Female"
GENDER_NONE = "None"
USER_GENDERS = [GENDER_NONE, GENDER_MALE, GENDER_FEMALE]
MAX_CHAT_BUTTON_CONTENT_LENGTH = 20
ASSISTANT_REPLY_STREAM_DELAY = 0.01
ASSISTANT_TITLE = "AI Psychological Assistant :robot_face:"
ASSISTANT_DESCRIPTION = """
:handshake: Meet your personal psychological therapist and assistant chatbot, here to support you through life's challenges.

:sparkles: Specializing in managing stress, depression, anxiety, fear, and apathy, this compassionate and confidential AI companion offers personalized advice.

:seedling: Empower yourself with tools to navigate your emotional well-being.

:speech_balloon: Create a new chat or choose an existing chat to start/continue a conversation.

:copyright: *Made by Ilia Filippov*
"""
