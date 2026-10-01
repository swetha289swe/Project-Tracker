from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import auth, project, project_members, users

tracker = FastAPI(title="Smart Project Tracker", version="0.1.0")

@tracker.exception_handler(Exception)
async def catch_all(request: Request, exc: Exception):
    import traceback
    traceback.print_exc()
    return JSONResponse(status_code=500, content={"detail": str(exc)})


tracker.include_router(auth.router)
tracker.include_router(users.router)
tracker.include_router(project.router)
tracker.include_router(project_members.router)


@tracker.get("/")
def root():
    return {"status": "ok"}


    # uv run uvicorn app.main:tracker  --reload