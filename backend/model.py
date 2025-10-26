import uuid
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from sqlalchemy import Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.dialects.postgresql import TEXT
from datetime import datetime, timezone
from pydantic import BaseModel


def generateUuidHex():
    return uuid.uuid4().hex


def getCurrTimestamp():
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    user_id: str = Field(default_factory=generateUuidHex, primary_key=True)
    username: Optional[str] = Field(default="")
    user_password: Optional[str] = Field(default="")
    user_gender: Optional[str] = Field(default=None)
    user_age: int | None = Field(default=None)
    chats: list["ChatElement"] = Relationship(back_populates="user")

    __table_args__ = (
        UniqueConstraint("username", "user_password", name="username_password_uk"),
   )


class ChatElement(SQLModel, table=True):
    chat_id: str = Field(default_factory=generateUuidHex, primary_key=True)
    chat_role: Optional[str] = Field(default="", primary_key=True)
    created_at: datetime = Field(default_factory=getCurrTimestamp, primary_key=True)
    chat_message: Optional[str] = Field(default="", sa_column=Column(TEXT))
    user_id: Optional[str] = Field(default=None, foreign_key="user.user_id")
    user: User | None = Relationship(back_populates="chats")

    __tablename__ = "chat_history"


class QueryResponseElement(BaseModel):
    is_rag_used: bool
    query: ChatElement
    response: Optional[ChatElement] = None
    chat_history: List[ChatElement] = []