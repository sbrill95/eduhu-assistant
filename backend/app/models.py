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


# ═══════════════════════════════════════
# Material / Klausur Models
# ═══════════════════════════════════════

class ExamTask(BaseModel):
    aufgabe: str
    beschreibung: str
    afb_level: str  # "I", "II", or "III"
    punkte: int
    erwartung: list[str]


class ExamStructure(BaseModel):
    fach: str
    klasse: str
    thema: str
    dauer_minuten: int
    aufgaben: list[ExamTask]
    gesamtpunkte: int
    notenschluessel: dict[str, str]
    hinweise: list[str]


class MaterialRequest(BaseModel):
    type: str  # "klausur" | "arbeitsblatt" | "differenzierung"
    fach: str
    klasse: str
    thema: str
    teacher_id: str
    dauer_minuten: Optional[int] = None
    afb_verteilung: Optional[dict[str, int]] = None
    zusatz_anweisungen: Optional[str] = None


class MaterialResponse(BaseModel):
    id: str
    type: str
    content: ExamStructure
    docx_url: Optional[str] = None
    created_at: str
