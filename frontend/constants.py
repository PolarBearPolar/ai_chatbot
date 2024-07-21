import os
import logging

BACKEND_BASE_URL = f"http://backend:{os.environ.get('BACKEND_PORT')}"
BACKEND_USER_ENDPOINT = "user"
BACKEND_QUERY_ENDPOINT = "query"
BACKEND_REQUEST_TIMEOUT = 20000
BACKEND_HEADER_LANGUAGE = "Accept-Language"
DEFAULT_LANGUAGE = os.environ.get("DEFAULT_LANGUAGE")
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(message)s"
LOG_FILE = "log.log"
ROLE_ASSISTANT = "ASSISTANT"
ROLE_USER = "USER"
CHAT_NEWLINE_CHARACTER = "  \n"
GENDER_MALE = "male"
GENDER_FEMALE = "female"
GENDER_NONE = "none"
MAX_CHAT_BUTTON_CONTENT_LENGTH = 20
ASSISTANT_REPLY_STREAM_DELAY = 0.01
APPLICATION_TITLE = "AI Psychological Assistant"
HEADER_COLOR = "#3EA99F"
ASSISTANT_TITLE_WRAPPER = "<h1 style='text-align: center; color: {color};'>🤖 {text} 👩‍⚕️</h1>"
ASSISTANT_WELCOMING_MESSAGE_WRAPPER="<h1 style='text-align: center; color: {color};'>{text}</h1>"
ASSISTANT_CHAT_DESCRIPTION_WRAPPER = "<p style='text-align: center; color: {color}; font-size: 20px;'><b>{text}</b></p>"
ASSISTANT_USAGE_DESCRIPTION_WRAPPER = "<p style='text-align: center; color: {color}; font-size: 20px;'><b>{text}</b></p>"
CSS_STYLE_ACTION_BUTTON = """
    button {
        outline: none;
        box-shadow: 
            inset 0 2px 0 rgba(0,0,0,.2), 
            0 0 4px rgba(0,0,0,0.1), 
            0 0 5px 1px #acfa1b;
    }
"""
IMAGE_PATH_LOGO = "static/images/logo.png"
IMAGE_PATH_WELCOME = "static/images/welcome.json"
IMAGE_PATH_CHAT_HISTORY = "static/images/chat_history.svg"
IMAGE_PATH_HELP = "static/images/help.json"
IMAGE_PATH_CHAT = "static/images/chat.json"
WEB_ELEMENT_TEXTS = {   
    "en": {
        "authentication":{
            "text_welcome": "You are just one step away from receiving the psycological support you need",
            "label_language_selectbox": "Select language",
            "selectbox_language_options" : {
                "en": "🇬🇧 English",
                "sr": "🇷🇸 Serbian",
                "ru": "🇷🇺 Russian"
            },
            "label_username": "Username:",
            "label_password": "Password:",
            "button_log_in": "Log in"
        }, 
        "chat": {
            "text_title": "AI Psychological Assistant",
            "text_chat_description": "Meet your personal psychological therapist and assistant chatbot, here to support you through life's challenges.",
            "text_usage_description": "Create a new chat to start a new conversation or choose an existing chat in the sidebar tab (you can open it in the top-left corner) to continue an existing conversation.",
            "text_wait": "Processing your query...",
            "button_start_chat": "START NEW CHAT",
            "button_delete_chat": "DELETE CURRENT CHAT",
            "placeholder_chat": "Ask your question here..."
        }, 
        "sidebar": {
            "label_user_information": "User Information",
            "label_gender_radio": "Gender",
            "radio_gender_options" : {
                "none": "None",
                "male": "Male",
                "female": "Female"
            },
            "label_age": "Age",
            "label_chat_history": "Chat History",
            "placeholder_age": "Type a number..."
        }
    },
    "sr": {
        "authentication":{
            "text_welcome": "Samo ste jedan korak od psihološke podrške koja vam je potrebna",
            "label_language_selectbox": "Izaberi jezik",
            "selectbox_language_options" : {
                "en": "🇬🇧 Engleski",
                "sr": "🇷🇸 Srpski",
                "ru": "🇷🇺 Ruski"
            },
            "label_username": "Korisničko ime:",
            "label_password": "Lozinka:",
            "button_log_in": "Prijavi se"
        }, 
        "chat": {
            "text_title": "AI psihološki asistent",
            "text_chat_description": "Upoznajte svog ličnog psihološkog terapeuta i pomoćnog chat bota, ovde da vas podrži kroz životne izazove.",
            "text_usage_description": "Kreirajte novo ćaskanje da biste započeli novu konverzaciju ili izaberite postojeće ćaskanje na kartici bočne trake (možete ga otvoriti u gornjem levom uglu) da biste nastavili postojeću konverzaciju.",
            "text_wait": "Obrada vašeg pitanja...",
            "button_start_chat": "ZAPOČNI NOVI ĆAT",
            "button_delete_chat": "IZBRIŠI TRENUTNO ĆAT",
            "placeholder_chat": "Postavite pitanje ovde..."
        }, 
        "sidebar": {
            "label_user_information": "Informacije o korisniku",
            "label_gender_radio": "Pol",
            "radio_gender_options" : {
                "none": "nije navedeno",
                "male": "muško",
                "female": "žensko"
            },
            "label_age": "Starost",
            "label_chat_history": "Istorija ćaskanja",
            "placeholder_age": "Unesite broj..."
        }
    },
    "ru": {
        "authentication":{
            "text_welcome": "Вы всего в одном шаге от получения необходимой вам психологической поддержки",
            "label_language_selectbox": "Выберите язык",
            "selectbox_language_options" : {
                "en": "🇬🇧 Английский",
                "sr": "🇷🇸 Сербский",
                "ru": "🇷🇺 Русский"
            },
            "label_username": "Имя пользователя:",
            "label_password": "Пароль:",
            "button_log_in": "Войти"
        }, 
        "chat": {
            "text_title": "ИИ психологический помощник",
            "text_chat_description": "Ваш личный психолог и чат-бот-помощник, который поддержит вас в жизненных трудностях.",
            "text_usage_description": "Создайте новый чат или выберите существующий чат из вашей истории на вкладке боковой панели (вы можете открыть историю в левом верхнем углу).",
            "text_wait": "Обработка вашего вопроса...",
            "button_start_chat": "НАЧАТЬ НОВЫЙ ЧАТ",
            "button_delete_chat": "УДАЛИТЬ ТЕКУЩИЙ ЧАТ",
            "placeholder_chat": "Задайте свой вопрос здесь..."
        }, 
        "sidebar": {
            "label_user_information": "Информация о пользователе",
            "label_gender_radio": "Пол",
            "radio_gender_options" : {
                "none": "Не указано",
                "male": "Мужской",
                "female": "Женский"
            },
            "label_age": "Возраст",
            "label_chat_history": "История",
            "placeholder_age": "Введите число..."
        }
    }
}
