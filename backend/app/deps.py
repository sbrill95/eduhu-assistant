from fastapi import Request, HTTPException, Security, Depends
from fastapi.security import APIKeyHeader
from app import db
from app.config import get_settings

# Simple auth scheme: expects "X-Teacher-ID" header for now 
# (simulating session token validation)
# In production, verify JWT token from Supabase Auth header
api_key_header = APIKeyHeader(name="X-Teacher-ID", auto_error=False)

async def get_current_teacher_id(
    request: Request, 
    x_teacher_id: str | None = Security(api_key_header)
) -> str:
    """
    Extract teacher_id from header.
    In a real app, decode the JWT from Authorization header.
    Current simplified implementation trusts X-Teacher-ID header sent by frontend
    only because we haven't implemented full JWT verification yet.
    """
    if not x_teacher_id:
        # Fallback: check query param? No, strict security.
        # Allow dev/debug loophole? No.
        raise HTTPException(
            status_code=401, 
            detail="Nicht authentifiziert (X-Teacher-ID fehlt)"
        )
    
    # Optional: Verify if teacher actually exists in DB
    # teacher = await db.select("teachers", filters={"id": x_teacher_id}, single=True)
    # if not teacher:
    #     raise HTTPException(401, "Ungültige Teacher-ID")
        
    return x_teacher_id
