"""E-Mail service — SMTP via Hetzner."""
import logging
from pathlib import Path
from app.config import get_settings
from app import db

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"


def _render(template_name: str, **kwargs: str) -> str:
    """Load an HTML template and replace {{key}} placeholders."""
    html = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    for key, value in kwargs.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html


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
        # DEV mode: print email to console so developers can grab links
        import re
        from datetime import datetime, timezone

        plain = re.sub(r"<[^>]+>", "", body).strip()
        plain = re.sub(r"\n\s*\n+", "\n", plain)
        logger.warning(
            "\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  📧  DEV MAIL (SMTP not configured)                        ║\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            f"║  To:      {recipient}\n"
            f"║  Subject: {subject}\n"
            "╠══════════════════════════════════════════════════════════════╣\n"
            f"{plain}\n"
            "╚══════════════════════════════════════════════════════════════╝"
        )
        await db.update("email_log", {
            "status": "sent",
            "attempts": 1,
            "sent_at": datetime.now(timezone.utc),
            "error_message": "DEV: printed to console",
        }, filters={"id": log_id})
        return True

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
            "sent_at": datetime.now(timezone.utc),
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


def _frontend_url() -> str:
    """Return frontend_url with a sensible local fallback."""
    url = get_settings().frontend_url
    return url if url else "http://localhost:5173"


async def send_verification_email(email: str, token: str) -> bool:
    """Send Double-Opt-In verification email."""
    url = f"{_frontend_url()}/verify?token={token}"
    body = _render("verify.html", url=url)
    return await send_email(email, "E-Mail bestätigen — eduhu", body, "verify")


async def send_reset_email(email: str, token: str) -> bool:
    """Send password reset email."""
    url = f"{_frontend_url()}/reset-password?token={token}"
    body = _render("reset.html", url=url)
    return await send_email(email, "Passwort zurücksetzen — eduhu", body, "reset")


async def send_magic_link_email(email: str, token: str) -> bool:
    """Send magic link login email."""
    url = f"{_frontend_url()}/magic-login?token={token}"
    body = _render("magic_link.html", url=url)
    return await send_email(email, "Dein Login-Link — eduhu", body, "magic_link")
