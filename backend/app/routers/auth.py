"""Auth router — registration, login, verification, password reset."""
import secrets
import logging
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from app import db
from app.models import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshRequest,
    TokenResponse,
    UserOut,
)
from app.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.email_service import send_verification_email, send_reset_email, send_magic_link_email

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/auth", tags=["Auth"])


@router.post("/register")
async def register(req: RegisterRequest):
    """Register a new account. Sends verification email.

    Account inactive until verified.
    """
    # Check if email already exists
    existing = await db.raw_fetch(
        "SELECT id, email_verified FROM teachers WHERE email = $1", req.email
    )
    if existing:
        if existing[0]["email_verified"]:
            raise HTTPException(409, "E-Mail ist bereits registriert")
        else:
            # Re-send verification for unverified account
            token = secrets.token_urlsafe(32)
            expires = datetime.now(timezone.utc) + timedelta(hours=24)
            await db.raw_fetch(
                "UPDATE teachers SET magic_link_token = $1, magic_link_expires = $2, password_hash = $3, name = $4 WHERE id = $5",
                token,
                expires,
                hash_password(req.password),
                req.name,
                existing[0]["id"],
            )
            sent = await send_verification_email(req.email, token)
            if not sent:
                logger.error("Verification email failed for %s (re-send)", req.email)
                raise HTTPException(502, "Verifizierungs-E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen.")
            return {"message": "Verifizierungs-E-Mail erneut gesendet"}

    # Create new teacher with email_verified=false
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)
    teacher = await db.insert("teachers", {
        "name": req.name,
        "email": req.email,
        "password_hash": hash_password(req.password),
        "role": "teacher",
        "email_verified": False,
        "magic_link_token": token,
        "magic_link_expires": expires,
    })

    # Ensure profile exists
    await db.upsert(
        "user_profiles",
        {"id": teacher["id"], "name": req.name},
        on_conflict="id",
    )

    sent = await send_verification_email(req.email, token)
    if not sent:
        logger.error("Verification email failed for %s (new registration)", req.email)
        raise HTTPException(502, "Verifizierungs-E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen.")
    return {"message": "Registrierung erfolgreich. Bitte E-Mail bestätigen."}


@router.get("/verify/{token}")
async def verify_email(token: str):
    """Verify email address via Double-Opt-In token."""
    teacher = await db.raw_fetch(
        "SELECT id FROM teachers WHERE magic_link_token = $1 AND magic_link_expires > $2",
        token,
        datetime.now(timezone.utc),
    )
    if not teacher:
        raise HTTPException(400, "Ungültiger oder abgelaufener Token")

    await db.raw_fetch(
        "UPDATE teachers SET email_verified = true, magic_link_token = NULL, magic_link_expires = NULL WHERE id = $1",
        teacher[0]["id"],
    )
    return {"message": "E-Mail bestätigt. Du kannst dich jetzt einloggen."}


@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    # Find teacher by email
    teachers = await db.raw_fetch(
        "SELECT id, name, email, password_hash, role, email_verified FROM teachers WHERE email = $1",
        req.email,
    )
    if not teachers:
        raise HTTPException(401, "Ungültige Anmeldedaten")
    teacher = teachers[0]

    if not teacher["email_verified"]:
        raise HTTPException(403, "E-Mail noch nicht bestätigt. Bitte prüfe dein Postfach.")

    # Magic link mode
    if req.request_magic_link:
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(minutes=15)
        await db.raw_fetch(
            "UPDATE teachers SET magic_link_token = $1, magic_link_expires = $2 WHERE id = $3",
            token,
            expires,
            teacher["id"],
        )
        sent = await send_magic_link_email(req.email, token)
        if not sent:
            logger.error("Magic link email failed for %s", req.email)
            raise HTTPException(502, "E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen.")
        return {"message": "Magic Link gesendet. Prüfe dein Postfach."}

    # Password mode
    if not req.password:
        raise HTTPException(400, "Passwort erforderlich")

    if not teacher["password_hash"] or not verify_password(req.password, teacher["password_hash"]):
        raise HTTPException(401, "Ungültige Anmeldedaten")

    access_token = create_access_token(teacher["id"], teacher["role"])
    refresh_token = create_refresh_token(teacher["id"])

    return LoginResponse(
        teacher_id=teacher["id"],
        name=teacher["name"],
        role=teacher["role"],
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/magic-login")
async def magic_login(token: str):
    """Login via magic link token."""
    teachers = await db.raw_fetch(
        "SELECT id, name, role FROM teachers WHERE magic_link_token = $1 AND magic_link_expires > $2",
        token,
        datetime.now(timezone.utc),
    )
    if not teachers:
        raise HTTPException(400, "Ungültiger oder abgelaufener Magic Link")
    teacher = teachers[0]

    # Clear magic link token
    await db.raw_fetch(
        "UPDATE teachers SET magic_link_token = NULL, magic_link_expires = NULL WHERE id = $1",
        teacher["id"],
    )

    access_token = create_access_token(teacher["id"], teacher["role"])
    refresh_token = create_refresh_token(teacher["id"])

    return LoginResponse(
        teacher_id=teacher["id"],
        name=teacher["name"],
        role=teacher["role"],
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/forgot-password")
async def forgot_password(req: ForgotPasswordRequest):
    """Send password reset email."""
    teachers = await db.raw_fetch(
        "SELECT id FROM teachers WHERE email = $1 AND email_verified = true", req.email
    )

    # Always return success (don't reveal if email exists)
    if teachers:
        token = secrets.token_urlsafe(32)
        expires = datetime.now(timezone.utc) + timedelta(hours=1)
        await db.raw_fetch(
            "UPDATE teachers SET reset_token = $1, reset_token_expires = $2 WHERE id = $3",
            token,
            expires,
            teachers[0]["id"],
        )
        sent = await send_reset_email(req.email, token)
        if not sent:
            logger.error("Password reset email failed for %s", req.email)

    return {"message": "Falls ein Account existiert, wurde eine E-Mail gesendet."}


@router.post("/reset-password")
async def reset_password(req: ResetPasswordRequest):
    """Reset password using token from email."""
    teachers = await db.raw_fetch(
        "SELECT id FROM teachers WHERE reset_token = $1 AND reset_token_expires > $2",
        req.token,
        datetime.now(timezone.utc),
    )
    if not teachers:
        raise HTTPException(400, "Ungültiger oder abgelaufener Token")

    if len(req.new_password) < 8:
        raise HTTPException(400, "Passwort muss mindestens 8 Zeichen lang sein")

    await db.raw_fetch(
        "UPDATE teachers SET password_hash = $1, reset_token = NULL, reset_token_expires = NULL WHERE id = $2",
        hash_password(req.new_password),
        teachers[0]["id"],
    )
    return {"message": "Passwort erfolgreich geändert."}


@router.post("/refresh", response_model=TokenResponse)
async def refresh(req: RefreshRequest):
    """Get new access token using refresh token."""
    payload = decode_token(req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(401, "Ungültiger Refresh-Token")

    teacher_id = payload["sub"]

    # Get current role from DB
    teachers = await db.raw_fetch("SELECT role FROM teachers WHERE id = $1", teacher_id)
    if not teachers:
        raise HTTPException(401, "Account nicht gefunden")

    access_token = create_access_token(teacher_id, teachers[0]["role"])
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserOut)
async def get_me(teacher_id: str = None):
    """Get current user info.

    NOTE: Will be updated to use JWT from deps.py in next MR.
    """
    # Temporary: accept teacher_id as query param until JWT integration MR
    from fastapi import Depends
    from app.deps import get_current_teacher_id

    # For now, still uses X-Teacher-ID header
    # Will be replaced with JWT Bearer in feature/auth-jwt-integration MR
    if not teacher_id:
        raise HTTPException(401, "Nicht authentifiziert")

    teachers = await db.raw_fetch(
        "SELECT id, name, email, role, email_verified FROM teachers WHERE id = $1",
        teacher_id
    )
    if not teachers:
        raise HTTPException(404, "Account nicht gefunden")
    t = teachers[0]

    return UserOut(
        id=t["id"],
        name=t["name"],
        email=t.get("email", ""),
        role=t.get("role", "teacher"),
        email_verified=t.get("email_verified", False),
    )
