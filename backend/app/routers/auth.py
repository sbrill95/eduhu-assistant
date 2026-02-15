from fastapi import APIRouter, HTTPException
from app import db
from app.models import LoginRequest, LoginResponse

router = APIRouter(prefix="/api/auth", tags=["Auth"])

@router.post("/login", response_model=LoginResponse)
async def login(req: LoginRequest):
    teacher = await db.select(
        "teachers",
        columns="id, name",
        filters={"password": req.password.strip()},
        single=True,
    )
    if not teacher:
        raise HTTPException(401, "Falsches Passwort")

    # Ensure profile exists
    await db.upsert(
        "user_profiles",
        {"id": teacher["id"], "name": teacher["name"]},
        on_conflict="id",
    )

    return LoginResponse(teacher_id=teacher["id"], name=teacher["name"])
