from fastapi import APIRouter, Depends
from app import db
from app.deps import get_current_teacher_id
from pydantic import BaseModel
from datetime import date, datetime, timezone
from typing import Optional

router = APIRouter(prefix="/api/todos", tags=["Todos"])


class TodoCreate(BaseModel):
    text: str
    due_date: Optional[date] = None
    priority: str = "normal"


class TodoUpdate(BaseModel):
    text: Optional[str] = None
    done: Optional[bool] = None
    due_date: Optional[date] = None
    priority: Optional[str] = None


@router.get("")
async def list_todos(
    teacher_id: str = Depends(get_current_teacher_id),
    done: Optional[bool] = None,
):
    filters: dict = {"teacher_id": teacher_id}
    if done is not None:
        filters["done"] = done
    todos = await db.select(
        "todos", filters=filters, order="due_date.asc.nullslast,created_at.desc"
    )
    return todos if isinstance(todos, list) else []


@router.post("")
async def create_todo(
    todo: TodoCreate, teacher_id: str = Depends(get_current_teacher_id)
):
    return await db.insert(
        "todos",
        {
            "teacher_id": teacher_id,
            "text": todo.text,
            "due_date": str(todo.due_date) if todo.due_date else None,
            "priority": todo.priority,
        },
    )


@router.patch("/{todo_id}")
async def update_todo(
    todo_id: str,
    update: TodoUpdate,
    teacher_id: str = Depends(get_current_teacher_id),
):
    data = {k: v for k, v in update.model_dump().items() if v is not None}
    if data.get("done"):
        data["completed_at"] = datetime.now(timezone.utc).isoformat()
    if "due_date" in data and data["due_date"]:
        data["due_date"] = str(data["due_date"])
    await db.update("todos", data, filters={"id": todo_id, "teacher_id": teacher_id})
    return {"updated": True}


@router.delete("/{todo_id}")
async def delete_todo(
    todo_id: str, teacher_id: str = Depends(get_current_teacher_id)
):
    await db.delete("todos", filters={"id": todo_id, "teacher_id": teacher_id})
    return {"deleted": True}
