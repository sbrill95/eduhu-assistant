"""Pydantic models for API requests/responses."""

from pydantic import BaseModel, EmailStr
from typing import Optional


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str


class LoginRequest(BaseModel):
    """Updated: supports email+password OR email+magic_link mode."""

    email: EmailStr
    password: Optional[str] = None
    request_magic_link: bool = False


class LoginResponse(BaseModel):
    teacher_id: str
    name: str
    role: str
    access_token: str
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class UserOut(BaseModel):
    id: str
    name: str
    email: str
    role: str
    email_verified: bool


class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[str] = None
    teacher_id: str
    attachment_base64: Optional[str] = None
    attachment_name: Optional[str] = None
    attachment_type: Optional[str] = None


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
    onboarding_completed: Optional[bool] = None


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


# ═══════════════════════════════════════
# Differenzierung Models
# ═══════════════════════════════════════

class DiffTask(BaseModel):
    aufgabe: str
    beschreibung: str
    hilfestellung: Optional[str] = None
    punkte: int


class DiffNiveau(BaseModel):
    niveau: str  # "Basis" | "Mittel" | "Erweitert"
    aufgaben: list[DiffTask]
    zeitaufwand_minuten: int
    hinweise: list[str]


class DifferenzierungStructure(BaseModel):
    fach: str
    klasse: str
    thema: str
    niveaus: list[DiffNiveau]  # Always 3: Basis, Mittel, Erweitert
    allgemeine_hinweise: list[str]


class MaterialRequest(BaseModel):
    type: str  # "klausur" | "arbeitsblatt" | "differenzierung"
    fach: str
    klasse: str
    thema: str
    teacher_id: str
    conversation_id: str = ""
    dauer_minuten: Optional[int] = None
    afb_verteilung: Optional[dict[str, int]] = None
    zusatz_anweisungen: Optional[str] = None


class MaterialResponse(BaseModel):
    id: str
    type: str
    content: dict  # ExamStructure or DifferenzierungStructure as dict
    docx_url: Optional[str] = None
    created_at: str


# ═══════════════════════════════════════
# H5P Models
# ═══════════════════════════════════════

class H5PExerciseRequest(BaseModel):
    teacher_id: str
    fach: str
    klasse: str
    thema: str
    exercise_type: str  # "mc", "drag-text", "summary" etc. or "auto"
    num_questions: int
    page_id: Optional[str] = None


class H5PExerciseResponse(BaseModel):
    exercise_id: str
    page_id: str
    access_code: str
    title: str
    page_url: str


class PageOut(BaseModel):
    id: str
    title: str
    access_code: str
    exercise_count: int


class PublicPage(BaseModel):
    id: str
    title: str
    access_code: str


class PublicExercise(BaseModel):
    id: str
    title: str
    h5p_type: str
    created_at: str


class PublicExerciseWithContent(PublicExercise):
    h5p_content: dict
