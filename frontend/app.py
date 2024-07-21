import streamlit as st
import constants
st.set_page_config(
    layout="wide", 
    page_title=constants.APPLICATION_TITLE, 
    page_icon = constants.IMAGE_PATH_LOGO
)
import requests
import time
import logging
import helper
from model import User, ChatElement
from urllib.parse import urljoin
from typing import Generator
from streamlit_lottie import st_lottie
from streamlit_extras.stylable_container import stylable_container

# Set up logging
logging.basicConfig(
	level=constants.LOG_LEVEL,
	format=constants.LOG_FORMAT,
	handlers=[
		logging.FileHandler(constants.LOG_FILE, mode="a")
	]
)
logger = logging.getLogger(__name__)


def initSessionState() -> None:
    if "user" not in st.session_state:
        st.session_state.user = None
    if "language" not in st.session_state:
        st.session_state.language = constants.DEFAULT_LANGUAGE
    if "selectBoxLanguage" not in st.session_state:
        st.session_state.selectBoxLanguage = None
    if "webElementTexts" not in st.session_state:
        st.session_state.webElementTexts = constants.WEB_ELEMENT_TEXTS.get(constants.DEFAULT_LANGUAGE)
    if "isChatModeOn" not in st.session_state:
        st.session_state.isChatModeOn = False
    if "chat" not in st.session_state:
        st.session_state.chat = None
    if "userChats" not in st.session_state:
        st.session_state.userChats = []
    if "chatElements" not in st.session_state:
        st.session_state.chatElements = []
    if "messages" not in st.session_state:
        st.session_state.messages = []


def authenticate() -> None:
    if len(st.session_state.username.strip()) > 0 and len(st.session_state.userPassword.strip()) > 0:
        userRequest = requests.get(
            urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_USER_ENDPOINT), 
            params={"username": st.session_state.username, "password": st.session_state.userPassword}
        )
        if userRequest.status_code == 200:
            st.session_state.user = User(**userRequest.json())
            logger.info(f"{st.session_state.user.username} is using application now...")
        elif userRequest.status_code == 404:
            user = User(
                username=st.session_state.username, 
                user_password=st.session_state.userPassword
            )
            userPostRequest = requests.post(
                urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_USER_ENDPOINT), 
                data=user.model_dump_json()
            )
            st.session_state.user = User(**userPostRequest.json())
            logger.info(f"{st.session_state.user.username} is using application now...")


def updateLanguage() -> None:
    st.session_state.language = st.session_state.selectBoxLanguage
    st.session_state.webElementTexts = constants.WEB_ELEMENT_TEXTS.get(st.session_state.language)


def updateUserState() -> None:
    if not st.session_state.user:
        return
    userRequest = requests.get(
        urljoin(constants.BACKEND_BASE_URL, f"{constants.BACKEND_USER_ENDPOINT}/{st.session_state.user.user_id}")
    )
    if userRequest.status_code == 200:
        st.session_state.user = User(**userRequest.json())


def updateGender() -> None:
    st.session_state.user.user_gender = st.session_state.gender
    userUpdateRequest = requests.put(
        urljoin(constants.BACKEND_BASE_URL, f"{constants.BACKEND_USER_ENDPOINT}/{st.session_state.user.user_id}"), 
        data=st.session_state.user.model_dump_json()
    )


def updateAge() -> None:
    st.session_state.user.user_age = st.session_state.age
    userUpdateRequest = requests.put(
        urljoin(constants.BACKEND_BASE_URL, f"{constants.BACKEND_USER_ENDPOINT}/{st.session_state.user.user_id}"), 
        data=st.session_state.user.model_dump_json()
    )


def getAvatar(role: str=None) -> str:
    avatar = "👩‍⚕️"
    if role == constants.ROLE_USER:
        if st.session_state.gender == constants.GENDER_MALE:
            avatar = "👦"
        elif st.session_state.gender == constants.GENDER_FEMALE:
            avatar = "👧"
        elif st.session_state.gender == constants.GENDER_NONE:
            avatar = "😐"
    return avatar


def openChat(chat: ChatElement=None) -> None:
    st.session_state.isChatModeOn = True
    st.session_state.chat = chat
    getChatElements()


def getUserChats() -> None:
    request = requests.get(
        urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_QUERY_ENDPOINT),
        params={"userId": st.session_state.user.user_id}
    )
    if request.status_code in (200, 307):
        st.session_state.userChats.clear()
        for userChat in request.json():
            st.session_state.userChats.append(ChatElement(**userChat))


def getChatButtonContent(chatMessage: str=None) -> str:
    if len(chatMessage) > constants.MAX_CHAT_BUTTON_CONTENT_LENGTH:
        return f"{chatMessage[:constants.MAX_CHAT_BUTTON_CONTENT_LENGTH]}..."
    else:
        return f"{chatMessage}..."


def messageGenerator(message: str) -> Generator[str, None, None]:
    for letter in message:
        time.sleep(constants.ASSISTANT_REPLY_STREAM_DELAY)
        yield letter


def fixNewLines(message: str) -> str:
    return message.replace("\n", constants.CHAT_NEWLINE_CHARACTER)


def displayChatElement(role: str=None, message: str=None, streamMessage: bool=False) -> None:
    if not role or not message:
        return
    messageParentElement = st
    if role == constants.ROLE_USER:
        chcol1, chcol2 = st.columns([1, 4])
        messageParentElement = chcol2
    with messageParentElement.chat_message(role, avatar=getAvatar(role)):
        if streamMessage:
            st.write_stream(messageGenerator(fixNewLines(message)))
        else:
            st.write(fixNewLines(message))


def getChatElementRole(role: str=None) -> str:
    if not role:
        return
    elif constants.ROLE_USER.lower() == role.lower():
        return constants.ROLE_USER
    elif constants.ROLE_ASSISTANT.lower() == role.lower():
        return constants.ROLE_ASSISTANT
    else:
        return


def getChatElements() -> None:
    st.session_state.messages = []
    if not st.session_state.user or not st.session_state.chat:
        return
    request = requests.get(
        urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_QUERY_ENDPOINT),
        params={"userId": st.session_state.user.user_id, "chatElementId": st.session_state.chat.chat_id}
    )
    if request.status_code == 200:
        for chatElementJson in request.json():
            chatElement = ChatElement(**chatElementJson)
            st.session_state.messages.append(
                {
                    "role": getChatElementRole(chatElement.chat_role),
                    "content": chatElement.chat_message
                }
            )


def processQuery(query: str=None) -> None:
    isNewChat = True if len(st.session_state.messages) == 0 else False
    chatElement = ChatElement(
        chat_id=None if st.session_state.chat is None else st.session_state.chat.chat_id,
        chat_role=constants.ROLE_USER,
        chat_message=query,
        user_id=st.session_state.user.user_id
    )
    displayChatElement(constants.ROLE_USER, query)
    st.session_state.messages.append(
        {
            "role": constants.ROLE_USER,
            "content": query
        }
    )
    if isNewChat:
        with st.sidebar:
            st.button(
                getChatButtonContent(chatElement.chat_message), 
                type="secondary", 
                key=f"chat_{chatElement.chat_id}", 
                disabled=True, 
                on_click=openChat, 
                args=[chatElement]
            )
    with st.spinner(st.session_state.webElementTexts["chat"]["text_wait"]):
        chatElementPostRequest = requests.post(
            urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_QUERY_ENDPOINT), 
            headers={constants.BACKEND_HEADER_LANGUAGE: st.session_state.language},
            data=chatElement.model_dump_json(),
            timeout=constants.BACKEND_REQUEST_TIMEOUT
        )
    if chatElementPostRequest.status_code == 200 and chatElementPostRequest.json() is not None:
        if not st.session_state.chat:
            st.session_state.chat = ChatElement(**chatElementPostRequest.json())
        displayChatElement(constants.ROLE_ASSISTANT, chatElementPostRequest.json()["chat_message"], True)
        st.session_state.messages.append(
            {
                "role": constants.ROLE_ASSISTANT,
                "content": chatElementPostRequest.json()["chat_message"]
            }
        )


def deleteChat() -> None:
    if not st.session_state.user or not st.session_state.chat:
        return
    requests.delete(
        urljoin(constants.BACKEND_BASE_URL, constants.BACKEND_QUERY_ENDPOINT),
        params={"userId": st.session_state.user.user_id, "chatElementId": st.session_state.chat.chat_id}
    )
    st.session_state.chat = None
    st.session_state.messages = []


def main():
    ### Main block of code ###
    # Initialize values in session state
    initSessionState()
    # Handle autentication and language preferences
    if not st.session_state.user:
        st.markdown(
            constants.ASSISTANT_WELCOMING_MESSAGE_WRAPPER.format(
                color=constants.HEADER_COLOR, 
                text=st.session_state.webElementTexts["authentication"]["text_welcome"]
            ), 
            unsafe_allow_html=True
        )
        st.selectbox(
            f"{st.session_state.webElementTexts['authentication']['label_language_selectbox']}:", 
            options=st.session_state.webElementTexts["authentication"]["selectbox_language_options"].keys(),
            format_func=lambda x: st.session_state.webElementTexts["authentication"]["selectbox_language_options"][x],
            index=helper.getKeyIndex(st.session_state.webElementTexts["authentication"]["selectbox_language_options"], st.session_state.language),
            placeholder=f"{st.session_state.webElementTexts['authentication']['label_language_selectbox']}...",
            key="selectBoxLanguage",
            on_change=updateLanguage
        )
        st.text_input(label=st.session_state.webElementTexts["authentication"]["label_username"], value="", key="username")
        st.text_input(label=st.session_state.webElementTexts["authentication"]["label_password"], value="", type="password", key="userPassword")
        st.button(st.session_state.webElementTexts["authentication"]["button_log_in"], type="primary", on_click=authenticate)
        st_lottie(
            helper.loadLottieAnimationFile(constants.IMAGE_PATH_WELCOME),
            quality="low",
            height=400
        )
    # Display chatbot view
    else:
        updateUserState()
        # Display header and description
        st.markdown(
            constants.ASSISTANT_TITLE_WRAPPER.format(
                color=constants.HEADER_COLOR, 
                text=st.session_state.webElementTexts["chat"]["text_title"]
            ), 
            unsafe_allow_html=True
        )
        st_lottie(
                helper.loadLottieAnimationFile(constants.IMAGE_PATH_HELP),
                quality="low",
                height=200
            )
        st.markdown(
            fixNewLines(
                constants.ASSISTANT_CHAT_DESCRIPTION_WRAPPER.format(
                    color=constants.HEADER_COLOR, 
                    text=st.session_state.webElementTexts["chat"]["text_chat_description"]
                ),
            ), 
            unsafe_allow_html=True
        )
        st_lottie(
                helper.loadLottieAnimationFile(constants.IMAGE_PATH_CHAT),
                quality="low",
                height=200
            )
        st.markdown(
            fixNewLines(
                constants.ASSISTANT_USAGE_DESCRIPTION_WRAPPER.format(
                    color=constants.HEADER_COLOR, 
                    text=st.session_state.webElementTexts["chat"]["text_usage_description"]
                ),
            ), 
            unsafe_allow_html=True
        )
        with stylable_container(
            key="action_button",
            css_styles=constants.CSS_STYLE_ACTION_BUTTON
        ):
            st.button(
                f"**{st.session_state.webElementTexts['chat']['button_start_chat']}**", 
                type="primary", 
                key="new_chat", 
                on_click=openChat, 
                use_container_width=True
            )
            if st.session_state.isChatModeOn:
                st.button(
                    f"**{st.session_state.webElementTexts['chat']['button_delete_chat']}**", 
                    type="primary", 
                    on_click=deleteChat, 
                    use_container_width=True
                )
        st.divider()
        # Display sidebar elements
        st.logo(constants.IMAGE_PATH_CHAT_HISTORY)
        with st.sidebar:
            # Display user personal information
            st.sidebar.markdown(f"# {st.session_state.webElementTexts['sidebar']['label_user_information']} :clipboard:")
            scol1, scol2 = st.sidebar.columns(2)
            scol1.radio(
                st.session_state.webElementTexts["sidebar"]["label_gender_radio"], 
                st.session_state.webElementTexts["sidebar"]["radio_gender_options"], 
                key="gender",
                format_func=lambda x: st.session_state.webElementTexts["sidebar"]["radio_gender_options"][x],
                index=helper.getKeyIndex(st.session_state.webElementTexts["sidebar"]["radio_gender_options"], st.session_state.user.user_gender), 
                on_change=updateGender
            )
            scol2.number_input(
                st.session_state.webElementTexts["sidebar"]["label_age"], 
                min_value=0, 
                placeholder=st.session_state.webElementTexts["sidebar"]["placeholder_age"], 
                key="age", 
                value=st.session_state.user.user_age, 
                on_change=updateAge
            )
            st.sidebar.divider()
            # Display chat history
            st.sidebar.markdown(f"# {st.session_state.webElementTexts['sidebar']['label_chat_history']} :speech_balloon:")
            getUserChats()
            for i, chat in enumerate(st.session_state.userChats):
                isButtonDisabled = False
                if st.session_state.chat is not None and chat.chat_id == st.session_state.chat.chat_id:
                    isButtonDisabled = True
                st.button(
                    getChatButtonContent(chat.chat_message), 
                    type="secondary", 
                    key=f"chat_{chat.chat_id}", 
                    disabled=isButtonDisabled, 
                    on_click=openChat, 
                    args=[chat]
                )
        # Display chat view
        if st.session_state.isChatModeOn:
            for message in st.session_state.messages:
                displayChatElement(message["role"], message["content"])
            if prompt := st.chat_input(st.session_state.webElementTexts["chat"]["placeholder_chat"]):
                processQuery(prompt)


if __name__ == "__main__":
    main()
