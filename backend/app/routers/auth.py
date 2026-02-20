"""Auth router — registration, login, verification, password reset, demo mode."""
import secrets
import logging
import uuid
import random
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, HTTPException
from app import db
from fastapi import Depends
from app.deps import get_current_teacher_id
from app.models import (
    RegisterRequest,
    LoginRequest,
    LoginResponse,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    RefreshRequest,
    TokenResponse,
    UserOut,
    DemoUpgradeRequest,
    DemoUpgradeCompleteRequest,
)
from app.auth_utils import hash_password, verify_password, create_access_token, create_refresh_token, decode_token
from app.email_service import send_verification_email, send_reset_email, send_magic_link_email, send_upgrade_email, send_invite_email

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


@router.get("/demo-status")
async def demo_status():
    """Check if demo mode is enabled (any admin has demo_mode=true)."""
    admins = await db.raw_fetch(
        "SELECT demo_mode FROM teachers WHERE role = 'admin' AND demo_mode = true LIMIT 1"
    )
    return {"demo_enabled": len(admins) > 0 if admins else False}


@router.post("/demo-start")
async def demo_start():
    """Create a temporary demo account (7-day TTL). Rate-limited to 10/hour globally."""
    # Check if demo mode is enabled
    admins = await db.raw_fetch(
        "SELECT id FROM teachers WHERE role = 'admin' AND demo_mode = true LIMIT 1"
    )
    if not admins:
        raise HTTPException(403, "Demo-Modus ist nicht aktiviert")

    # Rate limit: max 10 demo accounts per hour (simple check)
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent = await db.raw_fetch(
        "SELECT COUNT(*) as cnt FROM teachers WHERE role = 'demo' AND created_at > $1",
        one_hour_ago,
    )
    if recent and recent[0]["cnt"] >= 10:
        raise HTTPException(429, "Zu viele Demo-Accounts erstellt. Bitte später erneut versuchen.")

    # Create demo teacher
    demo_name = f"Demo-User {random.randint(1000, 9999)}"
    expires = datetime.now(timezone.utc) + timedelta(days=7)

    teacher = await db.insert("teachers", {
        "name": demo_name,
        "role": "demo",
        "email_verified": True,  # skip verification for demo
        "demo_expires_at": expires,
        "password_hash": hash_password(f"demo-{uuid.uuid4().hex}"),
    })

    # Create profile
    await db.upsert(
        "user_profiles",
        {"id": teacher["id"], "name": demo_name},
        on_conflict="id",
    )

    access_token = create_access_token(teacher["id"], "demo")
    refresh_token = create_refresh_token(teacher["id"])

    return LoginResponse(
        teacher_id=teacher["id"],
        name=demo_name,
        role="demo",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/demo-upgrade")
async def demo_upgrade(
    req: DemoUpgradeRequest,
    teacher_id: str = Depends(get_current_teacher_id),
):
    """Step 1: Save survey + email, send upgrade link."""
    # Verify caller is a demo user
    teachers = await db.raw_fetch(
        "SELECT id, role, name FROM teachers WHERE id = $1", teacher_id
    )
    if not teachers or teachers[0]["role"] != "demo":
        raise HTTPException(403, "Nur Demo-Accounts können upgegradet werden")

    # Check email uniqueness
    existing = await db.raw_fetch(
        "SELECT id FROM teachers WHERE email = $1", req.email
    )
    if existing:
        raise HTTPException(409, "E-Mail ist bereits registriert")

    # Save survey data
    has_survey = any([req.survey_useful, req.survey_material, req.survey_recommend, req.survey_feedback])
    if has_survey:
        await db.insert("demo_surveys", {
            "teacher_id": teacher_id,
            "useful": req.survey_useful,
            "material": req.survey_material,
            "recommend": req.survey_recommend,
            "feedback": req.survey_feedback,
        })

    # Set email on teacher + generate upgrade token
    token = secrets.token_urlsafe(32)
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    await db.raw_fetch(
        """UPDATE teachers
           SET email = $1, magic_link_token = $2, magic_link_expires = $3
           WHERE id = $4""",
        req.email, token, expires, teacher_id,
    )

    # Send upgrade email
    sent = await send_upgrade_email(req.email, token)
    if not sent:
        logger.error("Upgrade email failed for %s", req.email)
        raise HTTPException(502, "E-Mail konnte nicht gesendet werden. Bitte später erneut versuchen.")

    return {"message": "Wir haben dir eine E-Mail geschickt. Klicke auf den Link, um dein Konto zu aktivieren."}


@router.post("/demo-upgrade/complete", response_model=LoginResponse)
async def demo_upgrade_complete(req: DemoUpgradeCompleteRequest):
    """Step 2: Set password + name, convert demo → teacher."""
    # Validate token
    teachers = await db.raw_fetch(
        "SELECT id, name, role FROM teachers WHERE magic_link_token = $1 AND magic_link_expires > $2",
        req.token, datetime.now(timezone.utc),
    )
    if not teachers:
        raise HTTPException(400, "Ungültiger oder abgelaufener Link")

    teacher = teachers[0]
    if teacher["role"] != "demo":
        raise HTTPException(400, "Dieses Konto wurde bereits aktiviert")

    # Validate password
    if len(req.password) < 8:
        raise HTTPException(400, "Passwort muss mindestens 8 Zeichen lang sein")

    name = req.name.strip() or teacher["name"]

    # Upgrade: demo → teacher
    await db.raw_fetch(
        """UPDATE teachers
           SET password_hash = $1, name = $2, role = 'teacher',
               email_verified = true, demo_expires_at = NULL,
               magic_link_token = NULL, magic_link_expires = NULL
           WHERE id = $3""",
        hash_password(req.password), name, teacher["id"],
    )

    # Update profile
    await db.upsert(
        "user_profiles",
        {"id": teacher["id"], "name": name},
        on_conflict="id",
    )

    # Issue new tokens
    access_token = create_access_token(teacher["id"], "teacher")
    refresh_token = create_refresh_token(teacher["id"])

    return LoginResponse(
        teacher_id=teacher["id"],
        name=name,
        role="teacher",
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/invite-colleagues")
async def invite_colleagues(
    emails: list[str],
    teacher_id: str = Depends(get_current_teacher_id),
):
    """Send invitation emails to colleagues."""
    if not emails or len(emails) > 10:
        raise HTTPException(400, "Bitte 1–10 E-Mail-Adressen angeben")

    # Get sender name
    teachers = await db.raw_fetch(
        "SELECT name FROM teachers WHERE id = $1", teacher_id
    )
    sender_name = teachers[0]["name"] if teachers else "Ein Kollege"

    sent = 0
    for email in emails:
        email = email.strip()
        if not email or "@" not in email:
            continue
        ok = await send_invite_email(email, sender_name)
        if ok:
            sent += 1

    return {"sent": sent, "total": len(emails)}


@router.post("/demo-cleanup")
async def demo_cleanup(admin_key: str = ""):
    """Cleanup expired demo accounts. Called by cron job or admin.
    
    Accepts admin_key query param for cron job authentication.
    """
    from app.config import get_settings
    settings = get_settings()

    # Simple auth: must provide admin_key matching JWT_SECRET prefix or be called internally
    if admin_key != (settings.jwt_secret or "")[:16]:
        raise HTTPException(403, "Ungültiger Admin-Key")

    now = datetime.now(timezone.utc)
    expired = await db.raw_fetch(
        "SELECT id FROM teachers WHERE role = 'demo' AND demo_expires_at < $1", now
    )
    if not expired:
        return {"deleted": 0}

    count = 0
    for row in expired:
        tid = row["id"]
        try:
            # Cascade delete all related data
            await db.raw_fetch("DELETE FROM messages WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = $1)", tid)
            await db.raw_fetch("DELETE FROM session_logs WHERE conversation_id IN (SELECT id FROM conversations WHERE user_id = $1)", tid)
            await db.raw_fetch("DELETE FROM conversations WHERE user_id = $1", tid)
            await db.raw_fetch("DELETE FROM user_memories WHERE teacher_id = $1", tid)
            await db.raw_fetch("DELETE FROM generated_materials WHERE teacher_id = $1", tid)
            await db.raw_fetch("DELETE FROM exercises WHERE teacher_id = $1", tid)
            await db.raw_fetch("DELETE FROM exercise_pages WHERE teacher_id = $1", tid)
            await db.raw_fetch("DELETE FROM token_usage WHERE teacher_id = $1", tid)
            await db.raw_fetch("DELETE FROM user_profiles WHERE id = $1", tid)
            await db.raw_fetch("DELETE FROM teachers WHERE id = $1", tid)
            count += 1
        except Exception as e:
            logger.error(f"Demo cleanup failed for {tid}: {e}")

    logger.info(f"Demo cleanup: deleted {count} expired accounts")
    return {"deleted": count}


@router.post("/demo-toggle")
async def demo_toggle(enabled: bool, teacher_id: str = ""):
    """Toggle demo mode for the current admin. Requires admin role."""
    if not teacher_id:
        raise HTTPException(401, "Nicht authentifiziert")

    # Verify admin role
    admins = await db.raw_fetch(
        "SELECT id FROM teachers WHERE id = $1 AND role = 'admin'", teacher_id
    )
    if not admins:
        raise HTTPException(403, "Nur Admins können den Demo-Modus umschalten")

    await db.raw_fetch(
        "UPDATE teachers SET demo_mode = $1 WHERE id = $2", enabled, teacher_id
    )
    return {"demo_mode": enabled}


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
