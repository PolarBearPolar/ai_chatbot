from pydantic import BaseModel
from datetime import datetime

class User(BaseModel):
    user_id: str | None = None
    username: str
    user_password: str
    user_gender: str | None = None
    user_age: int | None = None

class ChatElement(BaseModel):
    chat_id: str | None = None
    chat_role: str
    chat_message: str
    created_at: datetime = None
    user_id: str | None = None