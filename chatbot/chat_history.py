import sqlite3
import uuid
from llama_index.core.llms import ChatMessage, MessageRole

class ChatHistory:

    CHAT_HISTORY_CREATE_TABLE = '''
        CREATE TABLE IF NOT EXISTS chat_history(
            chat_id TEXT NOT NULL,
            chat_role TEXT NOT NULL,
            chat_message TEXT NOT NULL
        )
    '''
    CHAT_HISTORY_GET_MESSAGES = '''
        SELECT chat_role
            , chat_message
        FROM chat_history
        WHERE chat_id = ?
    '''
    CHAT_HISTORY_INSERT_MESSAGES = '''
        INSERT INTO  chat_history (chat_id, chat_role, chat_message)
        VALUES (?, ?, ?)
    '''
    CHAT_HISTORY_CLEAR_HISTORY = '''
        DELETE FROM chat_history
    '''
    ROLE_ASSISTANT = "assistant"
    ROLE_HUMAN = "human"

    def __init__(self, chatDbPath: str):
        self.chatDbPath = chatDbPath
        self.conn = None
        self.cur = None

    
    def __getChatId(self, chatId: str):
        if chatId is None:
            chatId = uuid.uuid4().hex
        return chatId


    def __initConnection(self):
        self.conn = sqlite3.connect(self.chatDbPath)
        self.cur = self.conn.cursor()
        self.cur.execute(ChatHistory.CHAT_HISTORY_CREATE_TABLE)
        self.conn.commit()


    def __closeConnection(self):
        self.cur.close()
        self.conn.close()


    def __transformToChatMessage(self, message: tuple):
        role = None
        if message[0] == ChatHistory.ROLE_ASSISTANT:
            role = MessageRole.ASSISTANT
        elif message[0] == ChatHistory.ROLE_HUMAN:
            role = MessageRole.USER
        return ChatMessage(
            role=role,
            content=message[1],
        )


    def getMessages(self, chatId: str = None):
        chatId = self.__getChatId(chatId)
        self.__initConnection()
        messages = self.cur.execute(ChatHistory.CHAT_HISTORY_GET_MESSAGES, (chatId,)).fetchall()
        self.__closeConnection()
        transformedMessages = []
        for message in messages:
            transformedMessages.append(self.__transformToChatMessage(message))
        return (chatId, transformedMessages)


    def insertMessages(self, chatId: str, chatRole: str, chatMessage: str):
        if chatRole is None or chatMessage is None:
            return
        chatId = self.__getChatId(chatId)
        self.__initConnection()
        self.cur.execute(ChatHistory.CHAT_HISTORY_INSERT_MESSAGES, (chatId, chatRole, chatMessage))
        self.conn.commit()
        self.__closeConnection()
        return chatId
    

    def clearHistory(self):
        self.__initConnection()
        self.cur.execute(ChatHistory.CHAT_HISTORY_CLEAR_HISTORY)
        self.conn.commit()
        self.__closeConnection()

    


    
