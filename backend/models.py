from pydantic import BaseModel
from typing import Literal


class Message(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    model: str = "deepseek-chat"
    messages: list[Message]


class TutorRequest(BaseModel):
    message: str
