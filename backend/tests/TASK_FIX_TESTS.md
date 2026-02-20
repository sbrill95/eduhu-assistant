# Task: Fix all 27 failing backend tests

## Context
The app evolved (JWT auth, new material types, email-based login) but tests are outdated.

## Changes needed

### 1. `conftest.py` — Add JWT auth helper
The app now uses JWT Bearer auth (see `app/deps.py`). The `X-Teacher-ID` header no longer works.

Add to conftest.py:
```python
from app.auth_utils import create_access_token

def auth_headers(teacher_id: str = TEACHER_ID, role: str = "teacher") -> dict:
    """Generate JWT auth headers for testing."""
    token = create_access_token(teacher_id, role)
    return {"Authorization": f"Bearer {token}"}
```

Update the `client` fixture: instead of `ac.headers["X-Teacher-ID"] = TEACHER_ID`, use:
```python
token = create_access_token(TEACHER_ID, "teacher")
ac.headers["Authorization"] = f"Bearer {token}"
```

Also add a verified teacher to FakeDB's teachers table:
```python
"teachers": [{
    "id": TEACHER_ID, "name": TEACHER_NAME, "password": "test123",
    "email": "test@example.com", "password_hash": hash_password("test123"),
    "role": "teacher", "email_verified": True,
}],
```

### 2. `test_unit.py` — Fix LoginRequest tests
LoginRequest now requires `email` field:
```python
class LoginRequest(BaseModel):
    email: EmailStr
    password: Optional[str] = None
    request_magic_link: bool = False
```

Fix test_login_request_valid: add `email="test@example.com"`
Fix test_login_request_empty_password: add `email="test@example.com"`

### 3. `test_unit.py` — Fix material type alias tests
TYPE_ALIASES only maps: klassenarbeit→klausur, arbeitsblatt→versuchsanleitung, experiment→versuchsanleitung, unterrichtsplanung→stundenplanung, verlaufsplan→stundenplanung.

Unknown types are NOT mapped to klausur — they stay as-is.

Fix tests to match actual behavior:
- `resolve_material_type("test")` → `"test"` (not "klausur")
- `resolve_material_type("prüfung")` → `"prüfung"` (not "klausur")
- `resolve_material_type("differenziert")` → `"differenziert"` (not "differenzierung")
- `resolve_material_type("quiz")` → `"quiz"` (not "klausur")

Also add tests for actual aliases that DO work:
- `resolve_material_type("klassenarbeit")` → `"klausur"`
- `resolve_material_type("arbeitsblatt")` → `"versuchsanleitung"`

### 4. `test_integration.py` — Fix auth tests
Login endpoint is now POST `/api/auth/login` with body `{"email": "...", "password": "..."}`.

The FakeDB won't work for login tests because login uses `db.raw_fetch` with SQL. You need to mock `db.raw_fetch` to return teacher data for login tests.

For profile/chat/material tests: the client fixture already has JWT headers (from step 1), so those should work once auth is correct.

### 5. `test_security.py` — Fix auth-related security tests
Same issue: tests expect 403 for cross-teacher access but get 401 because JWT auth fails. With proper JWT headers they should work.

### 6. `test_agents.py` — Fix ExamStructure subscriptability
If tests do `structure["field"]`, use `structure.field` instead (Pydantic v2 models aren't subscriptable by default).

Also check that material service mocks return proper structures.

## Important constraints
- Do NOT change app code, only test files
- Keep FakeDB working for all tests
- Auth login tests need `db.raw_fetch` mocked since FakeDB.raw_fetch returns []
- Import `hash_password` from `app.auth_utils` in conftest
- Run `cd ~/eduhu-assistant/backend && .venv/bin/python -m pytest tests/test_unit.py tests/test_integration.py tests/test_security.py tests/test_agents.py -q --tb=short` to verify
