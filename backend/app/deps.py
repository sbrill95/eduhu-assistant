"""Authentication dependencies — JWT Bearer token validation."""
import os
import logging
from fastapi import Request, HTTPException, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Depends
from app.auth_utils import decode_token

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


async def get_current_teacher_id(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Extract and validate teacher_id from JWT Bearer token."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Ungültiger oder abgelaufener Token")

    if payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Ungültiger Token-Typ")

    teacher_id = payload.get("sub")
    if not teacher_id:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    return teacher_id


async def get_current_role(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Extract role from JWT. Returns 'teacher' as default."""
    if not credentials:
        return "teacher"

    payload = decode_token(credentials.credentials)
    if not payload:
        return "teacher"

    return payload.get("role", "teacher")


async def require_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    """Require admin role. Returns teacher_id if admin."""
    if not credentials:
        raise HTTPException(status_code=401, detail="Nicht authentifiziert")

    payload = decode_token(credentials.credentials)
    if not payload:
        raise HTTPException(status_code=401, detail="Ungültiger Token")

    if payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin-Rechte erforderlich")

    return payload.get("sub", "")


async def verify_admin(x_admin_secret: str = Header()):
    """Legacy admin verification via header secret. Keep for backward compat."""
    expected = os.environ.get("ADMIN_SECRET", "cleanup-2026")
    if x_admin_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
