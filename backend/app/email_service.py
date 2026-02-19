"""E-Mail service — SMTP via Hetzner."""
import logging
import re
import smtplib
from datetime import datetime, timezone
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from app.config import get_settings
from app import db

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent / "templates"

SMTP_TIMEOUT_SECONDS = 15


class _LoggingSMTP(smtplib.SMTP):
    """SMTP subclass that routes debug output to our logger instead of stderr."""

    def _print_debug(self, *args: object) -> None:
        logger.debug("SMTP >>> %s", " ".join(str(a) for a in args))


def _render(template_name: str, **kwargs: str) -> str:
    """Load an HTML template and replace {{key}} placeholders."""
    html = (TEMPLATE_DIR / template_name).read_text(encoding="utf-8")
    for key, value in kwargs.items():
        html = html.replace(f"{{{{{key}}}}}", value)
    return html


def _mask(value: str) -> str:
    """Mask a secret for safe logging: show first 2 and last 2 chars."""
    if len(value) <= 4:
        return "***"
    return f"{value[:2]}***{value[-2:]}"


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
        plain = re.sub(r"<[^>]+>", "", body).strip()
        plain = re.sub(r"\n\s*\n+", "\n", plain)
        logger.warning(
            "\n"
            "╔══════════════════════════════════════════════════════════════╗\n"
            "║  DEV MAIL (SMTP not configured)                            ║\n"
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

    logger.info(
        "SMTP send attempt: server=%s:%s, user=%s, from=%s, to=%s, type=%s",
        s.mail_server, s.mail_port, _mask(s.mail_username),
        s.mail_from, recipient, email_type,
    )

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{s.mail_from_name} <{s.mail_from}>"
        msg["To"] = recipient
        msg.attach(MIMEText(body, "html"))

        with _LoggingSMTP(s.mail_server, s.mail_port, timeout=SMTP_TIMEOUT_SECONDS) as server:
            server.set_debuglevel(1)
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(s.mail_username, s.mail_password)
            refused = server.send_message(msg)

        if refused:
            logger.warning("SMTP: some recipients refused: %s", refused)

        await db.update("email_log", {
            "status": "sent",
            "attempts": 1,
            "sent_at": datetime.now(timezone.utc),
        }, filters={"id": log_id})
        logger.info("Email sent successfully to %s (%s)", recipient, email_type)
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error("SMTP auth failed for user %s on %s:%s — %s",
                      s.mail_username, s.mail_server, s.mail_port, e)
        await _mark_failed(log_id, e)
        return False
    except smtplib.SMTPConnectError as e:
        logger.error("SMTP connect failed to %s:%s — %s",
                      s.mail_server, s.mail_port, e)
        await _mark_failed(log_id, e)
        return False
    except smtplib.SMTPException as e:
        logger.error("SMTP error sending to %s: %s", recipient, e)
        await _mark_failed(log_id, e)
        return False
    except OSError as e:
        logger.error("Network error connecting to %s:%s — %s",
                      s.mail_server, s.mail_port, e)
        await _mark_failed(log_id, e)
        return False
    except Exception as e:
        logger.error("Unexpected error sending email to %s: %s", recipient, e, exc_info=True)
        await _mark_failed(log_id, e)
        return False


async def _mark_failed(log_id: str, error: Exception) -> None:
    await db.update("email_log", {
        "status": "failed",
        "error_message": str(error)[:500],
        "attempts": 1,
    }, filters={"id": log_id})


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
