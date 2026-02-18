"""E-Mail service — SMTP via Hetzner."""
import logging
from app.config import get_settings
from app import db
logger = logging.getLogger(__name__)
async def send_email(recipient: str, subject: str, body: str, email_type: str) -> bool:
    """Send an email via SMTP and log to email_log table.

    Returns True if sent successfully, False otherwise.
    """
    s = get_settings()
    # Log to email_log
    log_entry = await db.insert("email_log", {
        "recipient": recipient,
        "type": email_type,
        "status": "queued",
        "attempts": 0,
    })
    log_id = log_entry["id"]

    if not s.mail_server or not s.mail_username:
        logger.warning(f"Mail not configured, skipping email to {recipient}")
        await db.update("email_log", {"status": "failed", "error_message": "SMTP not configured"}, filters={"id": log_id})
        return False

    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    from datetime import datetime, timezone

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.mail_from_name} <{s.mail_from}>"
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))

        with smtplib.SMTP(s.mail_server, s.mail_port) as server:
            server.starttls()
            server.login(s.mail_username, s.mail_password)
            server.send_message(msg)

        await db.update("email_log", {
            "status": "sent",
            "attempts": 1,
            "sent_at": datetime.now(timezone.utc).isoformat(),
        }, filters={"id": log_id})
        logger.info(f"Email sent to {recipient} ({email_type})")
        return True
    except Exception as e:
        logger.error(f"Failed to send email to {recipient}: {e}")
        await db.update("email_log", {
            "status": "failed",
            "error_message": str(e)[:500],
            "attempts": 1,
        }, filters={"id": log_id})
        return False


async def send_verification_email(email: str, token: str) -> bool:
    """Send Double-Opt-In verification email."""
    s = get_settings()
    verify_url = f"{s.frontend_url}/verify?token={token}"
    body = f"""
    <h2>Willkommen bei eduhu! 🦉</h2>
    <p>Bitte bestätige deine E-Mail-Adresse:</p>
    <p><a href="{verify_url}" style="background:#C8552D;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">E-Mail bestätigen</a></p>
    <p>Oder kopiere diesen Link: {verify_url}</p>
    <p>Der Link ist 24 Stunden gültig.</p>
    """
    return await send_email(email, "E-Mail bestätigen — eduhu", body, "verify")


async def send_reset_email(email: str, token: str) -> bool:
    """Send password reset email."""
    s = get_settings()
    reset_url = f"{s.frontend_url}/reset-password?token={token}"
    body = f"""
    <h2>Passwort zurücksetzen</h2>
    <p>Du hast angefordert, dein Passwort zurückzusetzen:</p>
    <p><a href="{reset_url}" style="background:#C8552D;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">Neues Passwort setzen</a></p>
    <p>Oder kopiere diesen Link: {reset_url}</p>
    <p>Der Link ist 1 Stunde gültig.</p>
    """
    return await send_email(email, "Passwort zurücksetzen — eduhu", body, "reset")


async def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link login email."""
    s = get_settings()
    login_url = f"{s.frontend_url}/magic-login?token={token}"
    body = f"""
    <h2>Dein Login-Link 🦉</h2>
    <p>Klicke hier, um dich bei eduhu anzumelden:</p>
    <p><a href="{login_url}" style="background:#C8552D;color:white;padding:12px 24px;border-radius:8px;text-decoration:none;font-weight:bold;">Jetzt einloggen</a></p>
    <p>Oder kopiere diesen Link: {login_url}</p>
    <p>Der Link ist 15 Minuten gültig.</p>
    """
    return await send_email(email, "Dein Login-Link — eduhu", body, "magic_link")
