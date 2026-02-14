"""Pydantic models for API requests/responses."""

from pydantic import BaseModel
from typing import Optional


class LoginRequest(BaseModel):
    password: str


class LoginResponse(BaseModel):
    teacher_id: str
    name: str


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    teacher_id: str


class ChatMessageOut(BaseModel):
    id: str
    role: str
    content: str
    timestamp: str


class ChatResponse(BaseModel):
    conversation_id: str
    message: ChatMessageOut


class ProfileUpdate(BaseModel):
    bundesland: Optional[str] = None
    schulform: Optional[str] = None
    faecher: Optional[list[str]] = None
    jahrgaenge: Optional[list[int]] = None


class ConversationOut(BaseModel):
    id: str
    title: Optional[str] = None
    updated_at: str
