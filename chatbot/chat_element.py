from pydantic import BaseModel


class ChatElement(BaseModel):
    isRagUsed: bool
    chatId: str | None = None
    query: str
    answer: str | None = None
    timeTaken: float | None = None