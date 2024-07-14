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
APPLICATION_TITLE = "AI Psychological Assistant"
ASSISTANT_TITLE = f"<h1 style='text-align: center; color: darkturquoise;'>🤖 {APPLICATION_TITLE} 👩‍⚕️</h1>"
ASSISTANT_WELCOMING_MESSAGE_1="<h1 style='text-align: center; color: darkturquoise;'>You are just one step away from receiving the psycological support you need</h1>"
ASSISTANT_DESCRIPTION_1 = "<p style='text-align: center; color: darkturquoise;'><b>Meet your personal psychological therapist and assistant chatbot, here to support you through life's challenges.</b></p>"
ASSISTANT_DESCRIPTION_2 = "<p style='text-align: center; color: darkturquoise;'><b>Create a new chat to start a new conversation or choose an existing chat in the sidebar tab (you can open it in the top-left corner) to continue an existing conversation.</b></p>"
CSS_STYLE_ACTION_BUTTON = """
    button {
        outline: none;
        box-shadow: 
            inset 0 2px 0 rgba(0,0,0,.2), 
            0 0 4px rgba(0,0,0,0.1), 
            0 0 5px 1px #51CBEE;
    }
"""
IMAGE_PATH_LOGO = "static/images/logo.png"
IMAGE_PATH_WELCOME = "static/images/welcome.json"
IMAGE_PATH_CHAT_HISTORY = "static/images/chat_history.svg"
IMAGE_PATH_HELP = "static/images/help.json"
IMAGE_PATH_CHAT = "static/images/chat.json"
