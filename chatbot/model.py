from config import Config
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from llama_index.core.llms import ChatMessage, MessageRole


class ChatElement(BaseModel):
    chat_id: Optional[str] = None
    chat_role: str
    chat_message: str
    created_at: Optional[datetime] = None
    user_id: Optional[str] = None


class QueryResponseElement(BaseModel):
    is_rag_used: bool
    query: ChatElement
    response: Optional[ChatElement] = None
    chat_history: List[ChatElement] = []

    def __transformToChatMessage(self, chatElement: ChatElement) -> ChatMessage:
        role = None
        if chatElement.chat_role == Config.ROLE_ASSISTANT:
            role = MessageRole.ASSISTANT
        elif chatElement.chat_role == Config.ROLE_USER:
            role = MessageRole.USER
        else:
            return None
        return ChatMessage(
            role=role,
            content=chatElement.chat_message
        )
    
    def getTransformedChatHistory(self):
        transformedChatHistory = []
        for chatElement in self.chat_history:
            chatMessage = self.__transformToChatMessage(chatElement)
            if not chatMessage:
                continue
            transformedChatHistory.append(chatMessage)
        return transformedChatHistory
