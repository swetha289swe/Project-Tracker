from fastapi import APIRouter, Depends, HTTPException

from app.ai.client import parse_task_text
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.ai import ParseTaskRequest, ParseTaskResponse

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/parse-task", response_model=ParseTaskResponse)
def parse_task(payload: ParseTaskRequest, current_user: User = Depends(get_current_user)):
    try:
        result = parse_task_text(payload.text)
    except Exception as e:
        print("AI ERROR:", repr(e))   # TEMP — remove once fixed
        raise HTTPException(status_code=502, detail="Could not parse task text right now")
    
    return ParseTaskResponse(**result)